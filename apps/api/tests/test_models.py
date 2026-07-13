from app.db.models import Agent, KnowledgeBase, KnowledgeSource


def test_model_table_names_are_stable():
    assert KnowledgeBase.__tablename__ == "knowledge_bases"
    assert KnowledgeSource.__tablename__ == "knowledge_sources"
    assert Agent.__tablename__ == "agents"
