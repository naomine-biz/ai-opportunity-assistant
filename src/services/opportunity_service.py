"""
オポチュニティ関連サービス
"""
from datetime import date, datetime
from typing import Dict, List, Optional
from uuid import UUID

from sqlmodel import Session, select

from core.logger import get_opportunity_logger
from db.session import get_session
from models.entity import Customer, Opportunity, OpportunityUser, User
from models.master import Stage

logger = get_opportunity_logger()


async def get_opportunity_by_id(opportunity_id: UUID, session: Session = None) -> Dict:
    """
    指定されたIDのオポチュニティ詳細を取得

    Args:
        opportunity_id: 取得するオポチュニティのID
        session: データベースセッション (省略可能)

    Returns:
        オポチュニティ詳細情報の辞書

    Raises:
        ValueError: オポチュニティが存在しない場合
    """
    # セッションがない場合は新しく取得
    if session is None:
        session = get_session()

    # オポチュニティを検索
    opportunity = session.get(Opportunity, opportunity_id)
    if not opportunity:
        logger.warning(f"Opportunity not found: {opportunity_id}")
        raise ValueError(f"Opportunity not found: {opportunity_id}")

    # 顧客情報を取得
    customer = session.get(Customer, opportunity.customer_id)

    # ステージ情報を取得
    stage = session.get(Stage, opportunity.stage_id)

    # 担当者情報を取得
    opportunity_users = session.exec(
        select(OpportunityUser).where(OpportunityUser.opportunity_id == opportunity_id)
    ).all()

    # 担当者とコラボレーターに分ける
    owners = []
    collaborators = []

    for opp_user in opportunity_users:
        user = session.get(User, opp_user.user_id)
        user_info = {"id": str(user.id), "name": user.name}

        if opp_user.role == "owner":
            owners.append(user_info)
        elif opp_user.role == "collaborator":
            collaborators.append(user_info)

    # レスポンス形式を整える
    response = {
        "id": str(opportunity.id),
        "customer": {
            "id": str(customer.id),
            "name": customer.name,
        },
        "title": opportunity.title,
        "amount": opportunity.amount,
        "stage": {
            "id": stage.id,
            "name": stage.name,
        },
        "expected_close_date": opportunity.expected_close_date.isoformat(),
        "owners": owners,
        "collaborators": collaborators,
        "created_at": opportunity.created_at.isoformat(),
        "updated_at": opportunity.updated_at.isoformat(),
    }

    logger.info(f"Retrieved opportunity: {opportunity_id}")
    return response


async def create_opportunity(opportunity_data: dict, session: Session = None) -> UUID:
    """
    新規オポチュニティを作成

    Args:
        opportunity_data: オポチュニティ作成データ
        session: データベースセッション (省略可能)

    Returns:
        作成されたオポチュニティのID

    Raises:
        ValueError: 必須フィールドがない、または参照先が存在しない場合
    """
    # セッションがない場合は新しく取得
    if session is None:
        session = get_session()
    # 必須フィールドを確認
    required_fields = [
        "customer_id",
        "title",
        "amount",
        "stage_id",
        "expected_close_date",
        "owners",
    ]
    for field in required_fields:
        if field not in opportunity_data:
            logger.warning(f"Missing required field: {field}")
            raise ValueError(f"Missing required field: {field}")

    # 顧客が存在するか確認
    customer = session.get(Customer, opportunity_data["customer_id"])
    if not customer:
        logger.warning(f"Customer not found: {opportunity_data['customer_id']}")
        raise ValueError(f"Customer not found: {opportunity_data['customer_id']}")

    # ステージが存在するか確認
    stage = session.get(Stage, opportunity_data["stage_id"])
    if not stage:
        logger.warning(f"Stage not found: {opportunity_data['stage_id']}")
        raise ValueError(f"Stage not found: {opportunity_data['stage_id']}")

    # オーナーが存在するか確認
    for owner_id in opportunity_data["owners"]:
        user = session.get(User, owner_id)
        if not user:
            logger.warning(f"Owner user not found: {owner_id}")
            raise ValueError(f"User not found: {owner_id}")

    # コラボレーターが存在するか確認（存在する場合）
    if "collaborators" in opportunity_data:
        for collab_id in opportunity_data["collaborators"]:
            user = session.get(User, collab_id)
            if not user:
                logger.warning(f"Collaborator user not found: {collab_id}")
                raise ValueError(f"User not found: {collab_id}")

    # オポチュニティを作成
    new_opportunity = Opportunity(
        customer_id=opportunity_data["customer_id"],
        title=opportunity_data["title"],
        amount=opportunity_data["amount"],
        stage_id=opportunity_data["stage_id"],
        expected_close_date=date.fromisoformat(opportunity_data["expected_close_date"]),
    )
    session.add(new_opportunity)
    session.commit()
    session.refresh(new_opportunity)

    # オーナー関係を作成
    for owner_id in opportunity_data["owners"]:
        owner_relation = OpportunityUser(
            opportunity_id=new_opportunity.id,
            user_id=owner_id,
            role="owner",
        )
        session.add(owner_relation)

    # コラボレーター関係を作成（存在する場合）
    if "collaborators" in opportunity_data:
        for collab_id in opportunity_data["collaborators"]:
            collab_relation = OpportunityUser(
                opportunity_id=new_opportunity.id,
                user_id=collab_id,
                role="collaborator",
            )
            session.add(collab_relation)

    session.commit()
    logger.info(f"Created opportunity: {new_opportunity.id}")

    return new_opportunity.id


async def update_opportunity(
    opportunity_id: UUID, update_data: dict, session: Session = None
) -> bool:
    """
    オポチュニティ情報を更新

    Args:
        opportunity_id: 更新するオポチュニティのID
        update_data: 更新するフィールドと値
        session: データベースセッション (省略可能)

    Returns:
        更新が行われたかどうか

    Raises:
        ValueError: オポチュニティが存在しない、または参照先が存在しない場合
    """
    # セッションがない場合は新しく取得
    if session is None:
        session = get_session()
    # オポチュニティが存在するか確認
    opportunity = session.get(Opportunity, opportunity_id)
    if not opportunity:
        logger.warning(f"Opportunity not found: {opportunity_id}")
        raise ValueError(f"Opportunity not found: {opportunity_id}")

    # 更新可能フィールド
    allowed_fields = ["stage_id", "amount", "title", "expected_close_date"]

    updated = False
    for field in allowed_fields:
        if field in update_data:
            # ステージIDが指定されている場合は存在確認
            if field == "stage_id":
                stage = session.get(Stage, update_data[field])
                if not stage:
                    logger.warning(f"Stage not found: {update_data[field]}")
                    raise ValueError(f"Stage not found: {update_data[field]}")

            # 日付フィールドの場合はdate型に変換
            if field == "expected_close_date":
                setattr(opportunity, field, date.fromisoformat(update_data[field]))
            else:
                setattr(opportunity, field, update_data[field])
            updated = True

    if updated:
        # 更新日時を設定
        opportunity.updated_at = datetime.utcnow()
        session.commit()
        logger.info(f"Updated opportunity: {opportunity_id}")

    return updated


async def delete_opportunity(opportunity_id: UUID, session: Session = None) -> bool:
    """
    オポチュニティを削除

    Args:
        opportunity_id: 削除するオポチュニティのID
        session: データベースセッション (省略可能)

    Returns:
        削除が成功したかどうか

    Raises:
        ValueError: オポチュニティが存在しない場合
    """
    # セッションがない場合は新しく取得
    if session is None:
        session = get_session()
    # オポチュニティが存在するか確認
    opportunity = session.get(Opportunity, opportunity_id)
    if not opportunity:
        logger.warning(f"Opportunity not found: {opportunity_id}")
        raise ValueError(f"Opportunity not found: {opportunity_id}")

    # 関連するOpportunityUserを削除
    opp_users = session.exec(
        select(OpportunityUser).where(OpportunityUser.opportunity_id == opportunity_id)
    ).all()

    for opp_user in opp_users:
        session.delete(opp_user)

    # オポチュニティを削除
    session.delete(opportunity)
    session.commit()

    logger.info(f"Deleted opportunity: {opportunity_id}")
    return True


async def search_opportunities(
    customer_id: Optional[UUID] = None,
    title: Optional[str] = None,
    stage_id: Optional[int] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    min_amount: Optional[int] = None,
    max_amount: Optional[int] = None,
    session: Session = None,
) -> List[Dict]:
    """
    オポチュニティを検索

    Args:
        customer_id: 顧客ID
        title: 案件名（部分一致）
        stage_id: ステージID
        from_date: 予想クロージング日開始
        to_date: 予想クロージング日終了
        min_amount: 金額下限（任意）
        max_amount: 金額上限（任意）
        session: データベースセッション

    Returns:
        検索条件に合致するオポチュニティのリスト
    """
    # 検索クエリを構築
    query = select(Opportunity)

    if customer_id:
        query = query.where(Opportunity.customer_id == customer_id)

    if title:
        query = query.where(Opportunity.title.contains(title))

    if stage_id:
        query = query.where(Opportunity.stage_id == stage_id)

    if from_date:
        query = query.where(Opportunity.expected_close_date >= from_date)

    if to_date:
        query = query.where(Opportunity.expected_close_date <= to_date)

    if min_amount:
        query = query.where(Opportunity.amount >= min_amount)

    if max_amount:
        query = query.where(Opportunity.amount <= max_amount)

    # セッションがない場合は新しく取得
    if session is None:
        session = get_session()

    # 検索実行
    opportunities = session.exec(query).all()

    # 検索結果をフォーマット
    result = []
    for opp in opportunities:
        customer = session.get(Customer, opp.customer_id)
        stage = session.get(Stage, opp.stage_id)

        result.append(
            {
                "id": str(opp.id),
                "customer": {
                    "id": str(customer.id),
                    "name": customer.name,
                },
                "title": opp.title,
                "amount": opp.amount,
                "stage": {
                    "id": stage.id,
                    "name": stage.name,
                },
                "expected_close_date": opp.expected_close_date.isoformat(),
            }
        )

    logger.info(f"Search opportunities: found {len(result)} results")
    return result
