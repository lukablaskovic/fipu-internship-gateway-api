from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app import models
from app import schemas
from app import utils
from app.db import get_db
from app import oauth2
from datetime import datetime

from app.connectors.baserow_service_connector import BW_get_data

from typing import List  # Add this import statement

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", status_code=status.HTTP_200_OK, response_model=schemas.UserOut)
def get_current_user(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    if current_user.account_type == "student":
        student = (
            db.query(models.Student)
            .filter(models.Student.id == current_user.id)
            .first()
        )
        return schemas.Student.model_validate(student.__dict__)
    elif current_user.account_type == "admin":
        admin = (
            db.query(models.Admin).filter(models.Admin.id == current_user.id).first()
        )
        return schemas.Admin.model_validate(admin.__dict__)
    else:
        raise HTTPException(status_code=400, detail="User account_type not recognized")
    
@router.patch("/update_password", status_code=status.HTTP_200_OK)
async def update_password(
    password_update: schemas.PasswordUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    if not utils.verify(password_update.old_password, current_user.password):
        return {"message": "Invalid old password. Please try again."}

    current_user.password = utils.hash(password_update.new_password)

    try:
        db.commit()
    except Exception as e:
        print("Error updating password", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating password - {e}",
        )
    return {"message": "Password updated successfully"}
    
@router.post("/send_message", status_code=status.HTTP_201_CREATED, response_model=schemas.Message)
def send_message(
    message: schemas.MessageCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    # Check if the sender is authorized to send messages
    if current_user.account_type != "admin" and current_user.account_type != "student":
        raise HTTPException(status_code=403, detail="Unauthorized to send messages")

    # Create an instance of the SQLAlchemy Message class
    message_db = models.Message(
        sender_id=current_user.id,
        receiver_id=message.receiver_id,
        content=message.content
    )

    # Set sender_id to the current user's id
    message_db.sender_id = current_user.id
    
    # Save the message to the database
    db.add(message_db)
    db.commit()
    db.refresh(message_db)

    # Retrieve the conversation from the database
    conversation_db = db.query(models.Conversation).filter(
        models.Conversation.id == message.conversation_id
    ).first()
    if conversation_db.user_1_id == current_user.id:
        conversation_db.user_1_last_message_read_id = message_db.id
    else:
        conversation_db.user_2_last_message_read_id = message_db.id

    conversation_db.timestamp = datetime.now()

    db.commit()
    db.refresh(conversation_db)

    return message_db



@router.get("/get_messages/{receiver_id}", status_code=status.HTTP_200_OK, response_model=List[schemas.Message])
def get_messages(
    receiver_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    # Check if the current user is authorized to retrieve messages
    if current_user.account_type != "admin" and current_user.account_type != "student":
        raise HTTPException(status_code=403, detail="Unauthorized to retrieve messages")

    # Check if the receiver_id is valid
    if db.query(models.User).filter(models.User.id == receiver_id).first() is None:
        raise HTTPException(status_code=404, detail="Receiver user not found")
    
    # Retrieve messages where the current user is the sender and the receiver is the specified user
    messages_sent = db.query(models.Message).filter(
        models.Message.sender_id == current_user.id,
        models.Message.receiver_id == receiver_id
    ).all()

    # Retrieve messages where the current user is the receiver and the sender is the specified user
    messages_received = db.query(models.Message).filter(
        models.Message.sender_id == receiver_id,
        models.Message.receiver_id == current_user.id
    ).all()

    # Combine and return both sets of messages
    return messages_sent + messages_received

@router.get("/get_last_message/{receiver_id}", status_code=status.HTTP_200_OK, response_model=schemas.Message)
def get_last_message(
    receiver_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    # Check if the current user is authorized to retrieve messages
    if current_user.account_type != "admin" and current_user.account_type != "student":
        raise HTTPException(status_code=403, detail="Unauthorized to retrieve messages")

    # Check if the receiver_id is valid
    if db.query(models.User).filter(models.User.id == receiver_id).first() is None:
        raise HTTPException(status_code=404, detail="Receiver user not found")

    # Retrieve the most recent message where the current user is the sender and the receiver is the specified user
    last_message_sent = db.query(models.Message).filter(
        models.Message.sender_id == current_user.id,
        models.Message.receiver_id == receiver_id
    ).order_by(models.Message.timestamp.desc()).first()

    print(last_message_sent)

    # Retrieve the most recent message where the current user is the receiver and the sender is the specified user
    last_message_received = db.query(models.Message).filter(
        models.Message.sender_id == receiver_id,
        models.Message.receiver_id == current_user.id
    ).order_by(models.Message.timestamp.desc()).first()

    # Determine the most recent message
    if last_message_sent and last_message_received:
        most_recent_message = max(last_message_sent, last_message_received, key=lambda x: x.timestamp)
    elif last_message_sent:
        most_recent_message = last_message_sent
    else:
        most_recent_message = last_message_received

    if most_recent_message is None:
        raise HTTPException(status_code=200, detail="No messages found")

    return most_recent_message

    


def get_all_users_info_except_current_user(
    current_user_id: int,
    db: Session
) -> List[dict]:
    users_info = db.query(models.User.id,  models.User.ime, models.User.prezime).filter(models.User.id != current_user_id).all()
    
    return [{'id': user.id, 'ime': user.ime, 'prezime': user.prezime} for user in users_info]

@router.get("/get_all_users_info", status_code=status.HTTP_200_OK, response_model=List[dict])
def get_all_users_info(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    print("test")
    users_info = get_all_users_info_except_current_user(current_user.id, db)
    return users_info



def get_admins_info(db: Session) -> List[dict]:
    admins_info = db.query(models.Admin.id, models.Admin.ime, models.Admin.prezime).all()
    
    return [{'id': admin.id, 'ime': admin.ime, 'prezime': admin.prezime} for admin in admins_info]

@router.get("/get_all_admins_info", status_code=status.HTTP_200_OK, response_model=List[dict])
def get_all_admins_info(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    # Check if the current user is an admin
    if current_user.account_type != "student":
        raise HTTPException(status_code=403, detail="Unauthorized to access admins information")

    admins_info = get_admins_info(db)
    return admins_info



@router.post("/add_conversation", status_code=status.HTTP_201_CREATED, response_model=schemas.Conversation)
def add_conversation(
    conversation: schemas.ConversationPost, 
    db: Session = Depends(get_db)
):
    # Check if a conversation between the users already exists
    existing_conversation = db.query(models.Conversation).filter(
        models.Conversation.user_1_id == conversation.user_1_id,
        models.Conversation.user_2_id == conversation.user_2_id
    ).first()
    
    if existing_conversation:
        raise HTTPException(status_code=400, detail="Conversation already exists")

    # Create an instance of the SQLAlchemy Conversation class
    conversation_db = models.Conversation(
        user_1_id=conversation.user_1_id,
        user_2_id=conversation.user_2_id,
        status=conversation.status,
        user_1_last_message_read_id=conversation.user_1_last_message_read_id,
        user_2_last_message_read_id=conversation.user_2_last_message_read_id,
        user_1_active=conversation.user_1_active,
        user_2_active=conversation.user_2_active
    )
    
    # Save the conversation to the database
    db.add(conversation_db)
    db.commit()
    db.refresh(conversation_db)
    return conversation_db

@router.get("/get_conversations/{user_id}", response_model=List[schemas.Conversation])
def get_conversations(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    # Check if the current user is authorized to retrieve conversations
    if current_user.account_type != "admin" and current_user.account_type != "student":
        raise HTTPException(status_code=403, detail="Unauthorized to retrieve conversations")
    
    # Check if the user_id parameter matches the current user's id
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized to retrieve conversations for this user")

    # Retrieve conversations where the user is involved
    conversations = db.query(models.Conversation).filter(
        or_(
            models.Conversation.user_1_id == user_id,
            models.Conversation.user_2_id == user_id
        )
    ).all()

    return conversations

@router.patch("/update_conversation/{conversation_id}", response_model=schemas.Conversation)
def update_conversation(
    conversation_id: int,
    conversation_update: schemas.ConversationUpdate, 
    db: Session = Depends(get_db)
):
    # Retrieve the conversation from the database
    conversation_db = db.query(models.Conversation).filter(
        models.Conversation.id == conversation_id
    ).first()

    if not conversation_db:
        raise HTTPException(status_code=404, detail="Conversation not found")

    print(conversation_update)

    # Update the conversation attributes
    if conversation_update.status is not None:
        conversation_db.status = conversation_update.status

    if conversation_update.user_1_last_message_read_id is not None:
        if conversation_db.user_1_last_message_read_id != conversation_update.user_1_last_message_read_id:
            conversation_db.user_1_last_message_read_id = conversation_update.user_1_last_message_read_id
            conversation_db.timestamp = datetime.now()

    if conversation_update.user_2_last_message_read_id is not None:
        if conversation_db.user_2_last_message_read_id != conversation_update.user_2_last_message_read_id:
            conversation_db.user_2_last_message_read_id = conversation_update.user_2_last_message_read_id
            conversation_db.timestamp = datetime.now()

    if conversation_update.user_1_active is not None:
        if conversation_db.user_1_active != conversation_update.user_1_active:
            conversation_db.user_1_active = conversation_update.user_1_active
            conversation_db.timestamp = datetime.now()

    if conversation_update.user_2_active is not None:
        if conversation_db.user_2_active != conversation_update.user_2_active:
            conversation_db.user_2_active = conversation_update.user_2_active
            conversation_db.timestamp = datetime.now()


    # Save the updated conversation to the database
    db.commit()
    db.refresh(conversation_db)
    return conversation_db