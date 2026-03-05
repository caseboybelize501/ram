from neo4j import GraphDatabase
import os


class Neo4jStore:
    def __init__(self):
        uri = "bolt://localhost:7687"
        user = "neo4j"
        password = os.getenv("NEO4J_PASSWORD", "password")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_entity_node(self, entity_type, name, properties=None):
        with self.driver.session() as session:
            query = """
            MERGE (e:{entity_type} {name: $name})
            SET e += $properties
            RETURN e
            """
            result = session.run(query, name=name, properties=properties or {})
            return result.single()[0]

    def create_relationship(self, source_node, target_node, rel_type, properties=None):
        with self.driver.session() as session:
            query = """
            MATCH (a), (b)
            WHERE a.name = $source AND b.name = $target
            MERGE (a)-[r:{rel_type}]->(b)
            SET r += $properties
            RETURN r
            """
            result = session.run(query, source=source_node, target=target_node,
                               rel_type=rel_type, properties=properties or {})
            return result.single()[0]

    def get_top_entities(self):
        with self.driver.session() as session:
            query = """
            MATCH (e) 
            RETURN e.name AS name, count(*) AS count
            ORDER BY count DESC
            LIMIT 20
            """
            result = session.run(query)
            return [record["name"] for record in result]

    def get_related_entities(self, entity_name):
        with self.driver.session() as session:
            query = """
            MATCH (e)-[r]->(other)
            WHERE e.name = $entity_name
            RETURN other.name AS related_entity
            """
            result = session.run(query, entity_name=entity_name)
            return [record["related_entity"] for record in result]