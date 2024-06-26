from fastapi import HTTPException, Depends
from models.workflow import StartNode, EndNode, MessageNode, ConditionNode, Node
from schemas.workflow import *
from sqlalchemy.orm import Session
from database import get_db


class NodeService:
    """
    Service provides basic nodes management (get, create, update, delete)
    """

    def get_node(node_id: int, db: Session = Depends(get_db)):
        node = db.query(Node).filter(Node.id == node_id).first()
        if node:
            if node.node_type == 'start':
                return StartNodeSchema(workflow_id=node.workflow_id, next_node_id=node.next_node_id)
            elif node.node_type == 'message':
                return MessageNodeSchema(workflow_id=node.workflow_id, message_text=node.message_text, status=node.status, next_node_id=node.next_node_id)
            elif node.node_type == 'condition':
                return ConditionNodeSchema(workflow_id=node.workflow_id, condition=node.condition, yes_node_id=node.yes_node_id, no_node_id=node.no_node_id)
            else:
                return EndNodeSchema(workflow_id=node.workflow_id)
        else:
            return None


    def create_node(node_type: str, data: dict, db: Session = Depends(get_db())):
        if node_type == 'start':
            start_node = db.query(StartNode).filter(StartNode.workflow_id == data.workflow_id).first()
            if not start_node:  # if start node doesn`t exists (for specific workflow)
                node = StartNode(node_type=node_type, workflow_id=data.workflow_id, next_node_id=data.next_node_id)
            else:
                return False
            
        elif node_type == 'message':
            node = MessageNode(node_type=node_type, workflow_id=data.workflow_id, message_text=data.message_text, status=data.status, next_node_id=data.next_node_id)

        elif node_type == 'condition':
            node = ConditionNode(node_type=node_type, workflow_id=data.workflow_id, condition=data.condition, yes_node_id=data.yes_node_id, no_node_id=data.no_node_id)

        elif node_type == 'end':
            end_node = db.query(EndNode).filter(EndNode.workflow_id == data.workflow_id).first()
            if not end_node: # if end node doesn`t exists (for specific workflow)
                node = EndNode(node_type=node_type, workflow_id=data.workflow_id)
            else:
                return False
            
        db.add(node)
        db.commit()
        db.refresh(node)

        return node
    
    def update_node(node_id: int, data: dict, db: Session = Depends(get_db)):
        node = db.query(Node).filter(Node.id == node_id).first()
        if node.node_type == 'start':
            node.next_node_id = data.next_node_id
        elif node.node_type == 'message':
            node.workflow_id = data.workflow_id
            node.message_text = data.message_text
            node.status = data.status
            node.next_node_id = data.next_node_id
        elif node.node_type == 'condition':
            node.workflow_id = data.workflow_id
            node.condition = data.condition
            node.yes_node_id = data.yes_node_id
            node.no_node_id = data.no_node_id
        elif node.node_type == 'end':
            node.workflow_id=data.workflow_id

        db.add(node)
        db.commit()
        db.refresh(node)

        return node
    
    def delete_node(node_id: int, db: Session = Depends(get_db())):
        node = db.query(Node).filter(Node.id == node_id).first()
        if node:
            db.delete(node)
            db.commit()
            return True
        else:
            raise HTTPException(status_code=400, detail=f'Node with id {node_id} is not exists.')
    
        