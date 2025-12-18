#!/usr/bin/env python3
"""
聊天相关路由
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from typing import List, Optional
from backend.models import ChatRequest, ChatResponse, MessageUpdateRequest
from backend.services.chat_service import ChatService
from backend.logging_config import get_logger
import json
from pathlib import Path
import uuid
import os
import sys
import PyPDF2
import requests
from bs4 import BeautifulSoup

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

router = APIRouter(prefix="/chat", tags=["聊天"])
logger = get_logger(__name__)

# 初始化服务
chat_service = ChatService()

# 文件存储配置
UPLOAD_DIR = Path(project_root) / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# 支持的文件类型
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.txt', '.doc', '.docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def is_allowed_file(filename):
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    """从PDF文件中提取文本"""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        logger.error(f"PDF文本提取失败: {e}")
        return ""

def extract_text_from_image(file_path):
    """从图片中提取文本（OCR功能，这里简化处理）"""
    try:
        # 这里可以集成OCR库如pytesseract
        # 暂时返回占位符
        return "[图片内容 - 需要OCR处理]"
    except Exception as e:
        logger.error(f"图片文本提取失败: {e}")
        return ""

def parse_url_content(url):
    """解析URL内容"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 提取标题
        title = soup.find('title')
        title_text = title.get_text().strip() if title else "无标题"
        
        # 提取主要内容
        content_selectors = [
            'article', 'main', '.content', '.post-content', 
            '.entry-content', 'p', 'div'
        ]
        
        content_text = ""
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                content_text = " ".join([elem.get_text().strip() for elem in elements[:5]])
                break
        
        return {
            "url": url,
            "title": title_text,
            "content": content_text[:1000],  # 限制长度
            "status": "success"
        }
    except Exception as e:
        logger.error(f"URL解析失败: {e}")
        return {
            "url": url,
            "title": "解析失败",
            "content": f"无法解析URL内容: {str(e)}",
            "status": "error"
        }


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    聊天接口（启用记忆系统）
    """
    try:
        response = await chat_service.chat(request, use_memory_system=True)
        return response
    except Exception as e:
        logger.error(f"聊天接口错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simple", response_model=ChatResponse)
async def chat_simple(request: ChatRequest):
    """
    简单聊天接口（不使用记忆系统，用于对比）
    """
    try:
        response = await chat_service.chat(request, use_memory_system=False)
        return response
    except Exception as e:
        logger.error(f"简单聊天接口错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/summary")
async def get_session_summary(session_id: str):
    """获取会话摘要"""
    try:
        summary = await chat_service.get_session_summary(session_id)
        if "error" in summary:
            raise HTTPException(status_code=404, detail=summary["error"])
        return summary
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取会话摘要错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/history")
async def get_session_history(session_id: str, limit: int = 20):
    """获取会话历史"""
    try:
        history = await chat_service.get_session_history(session_id, limit)
        # 如果没有消息，返回空列表而不是404
        # 这样前端可以正常处理空会话的情况
        if not history.get("messages"):
            return {
                "session_id": session_id,
                "messages": []
            }
        return history
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取会话历史错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/sessions")
async def get_user_sessions(user_id: str, limit: int = 50):
    """获取用户的所有会话列表"""
    try:
        sessions = await chat_service.get_user_sessions(user_id, limit)
        return sessions
    except Exception as e:
        logger.error(f"获取用户会话列表错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/sessions/search")
async def search_user_sessions(user_id: str, keyword: str = "", limit: int = 50):
    """搜索用户会话"""
    try:
        result = await chat_service.search_user_sessions(user_id, keyword, limit)
        return result
    except Exception as e:
        logger.error(f"搜索用户会话错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/batch-delete")
async def delete_sessions_batch(session_ids: List[str]):
    """
    批量删除会话
    """
    try:
        if not session_ids:
            raise HTTPException(status_code=400, detail="会话ID列表不能为空")
        
        result = await chat_service.delete_sessions_batch(session_ids)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量删除会话错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/messages/{message_id}")
async def update_message(message_id: str, request: MessageUpdateRequest):
    """
    修改消息内容（消息编辑功能）
    支持类似ChatGPT/Gemini的编辑体验：
    1. 更新消息内容
    2. 删除该消息之后的所有消息
    3. 重新生成对话
    4. 更新向量数据库
    """
    try:
        # 输入验证
        if not request.new_content or not request.new_content.strip():
            raise HTTPException(status_code=400, detail="消息内容不能为空")
        
        if len(request.new_content.strip()) > 2000:
            raise HTTPException(status_code=400, detail="消息内容过长，最多2000字符")
        
        from backend.database import DatabaseManager
        
        with DatabaseManager() as db:
            # 尝试将message_id转换为整数，如果失败则保持字符串
            try:
                message_id_int = int(message_id)
            except ValueError:
                message_id_int = message_id
            
            # 1. 获取要编辑的消息
            original_message = db.get_message(message_id_int, request.user_id)
            if not original_message:
                raise HTTPException(status_code=404, detail="消息不存在或无权修改")
            
            session_id = original_message.session_id
            message_timestamp = original_message.created_at
            
            # 2. 删除该消息之后的所有消息（包括AI回复）
            from backend.database import ChatMessage
            deleted_count = db.db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id,
                ChatMessage.created_at > message_timestamp
            ).delete()
            
            # 3. 更新消息内容
            updated_message = db.update_message(
                message_id=message_id_int,
                user_id=request.user_id,
                new_content=request.new_content.strip(),
                emotion=request.emotion,
                emotion_intensity=request.emotion_intensity
            )
            
            # 4. 更新向量数据库（删除相关记录）
            try:
                from backend.vector_store import VectorStore
                vector_store = VectorStore()
                # 删除该会话在该时间点之后的向量记录
                # 注意：这里需要根据你的向量数据库实现来调整
                vector_store.delete_conversation_after_timestamp(session_id, message_timestamp)
            except Exception as e:
                logger.warning(f"更新向量数据库失败: {e}")
            
            # 5. 重新生成对话（类似ChatGPT/Gemini的行为）
            try:
                from backend.models import ChatRequest
                
                # 创建新的聊天请求，但不保存用户消息（因为已经更新了）
                new_request = ChatRequest(
                    message=request.new_content.strip(),
                    user_id=request.user_id,
                    session_id=session_id,
                    emotion=request.emotion,
                    emotion_intensity=request.emotion_intensity
                )
                
                # 直接调用聊天服务生成新的AI回复
                # 这会触发完整的对话流程：情感分析、上下文构建、RAG增强、记忆处理等
                response = await chat_service._generate_ai_response_for_edited_message(
                    new_request, updated_message
                )
                
                return {
                    "message": "消息编辑成功，已重新生成对话",
                    "message_id": updated_message.id,
                    "content": updated_message.content,
                    "updated_at": updated_message.created_at.isoformat() if updated_message.created_at else None,
                    "new_response": {
                        "content": response.response,
                        "emotion": response.emotion,
                        "suggestions": response.suggestions if hasattr(response, 'suggestions') else [],
                        "context": response.context if hasattr(response, 'context') else {},
                        "ai_message_id": response.ai_message_id if hasattr(response, 'ai_message_id') else None
                    },
                    "deleted_messages_count": deleted_count,
                    "regenerated": True
                }
                
            except Exception as e:
                logger.error(f"重新生成对话失败: {e}")
                import traceback
                traceback.print_exc()
                # 即使重新生成失败，消息编辑仍然成功
                return {
                    "message": "消息编辑成功，但重新生成对话失败",
                    "message_id": updated_message.id,
                    "content": updated_message.content,
                    "updated_at": updated_message.created_at.isoformat() if updated_message.created_at else None,
                    "error": "重新生成对话失败，请手动发送消息继续对话",
                    "deleted_messages_count": deleted_count
                }
            
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"修改消息错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


from fastapi import Query

@router.delete("/messages/{message_id}")
async def delete_message(message_id: str, user_id: str = Query(...)):
    """
    删除（撤回）消息
    只允许删除最近的一条用户消息
    """
    try:
        logger.info(f"收到删除消息请求: message_id={message_id}, user_id={user_id}")
        
        from backend.database import DatabaseManager, ChatMessage
        
        with DatabaseManager() as db:
            # 尝试将message_id转换为整数，如果失败则保持字符串
            try:
                message_id_int = int(message_id)
                logger.info(f"消息ID转换成功: {message_id} -> {message_id_int}")
            except ValueError:
                message_id_int = message_id
                logger.warning(f"消息ID转换失败，保持原值: {message_id}")
            
            # 先检查消息是否存在
            message = db.get_message(message_id_int, user_id)
            if not message:
                logger.warning(f"消息不存在或无权删除: message_id={message_id_int}, user_id={user_id}")
                raise HTTPException(status_code=404, detail="消息不存在或无权删除")
            
            # 检查是否为用户消息
            if message.role != 'user':
                logger.warning(f"只能删除用户消息: message_id={message_id_int}, role={message.role}")
                raise HTTPException(status_code=403, detail="只能删除自己发送的消息")
            
            logger.info(f"找到用户消息: {message.id}, 内容: {message.content[:50]}...")
            
            # 检查是否为该会话中最近的一条用户消息
            latest_user_message = db.db.query(ChatMessage).filter(
                ChatMessage.session_id == message.session_id,
                ChatMessage.user_id == user_id,
                ChatMessage.role == 'user'
            ).order_by(ChatMessage.created_at.desc()).first()
            
            if not latest_user_message or latest_user_message.id != message.id:
                logger.warning(f"只能删除最近的一条用户消息: message_id={message_id_int}, latest_id={latest_user_message.id if latest_user_message else None}")
                raise HTTPException(status_code=403, detail="只能撤回最近发送的一条消息")
            
            logger.info(f"验证通过，这是最近的用户消息: {message.id}")
            
            # 执行删除
            result = db.delete_message(message_id=message_id_int, user_id=user_id)
            
            if not result.get("success"):
                error_msg = result.get("error", "删除消息失败")
                logger.error(f"删除消息失败: message_id={message_id_int}, user_id={user_id}, error={error_msg}")
                raise HTTPException(status_code=500, detail=error_msg)
            
            deleted_count = result.get("deleted_count", 1)
            deleted_messages = result.get("deleted_messages", [])
            
            logger.info(f"消息删除成功: message_id={message_id_int}, 删除了 {deleted_count} 条消息")
            return {
                "message": "消息撤回成功",
                "message_id": message_id,
                "deleted_count": deleted_count,
                "deleted_messages": deleted_messages
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除消息错误: {e}")
        import traceback
        logger.error(f"错误堆栈: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """删除会话"""
    try:
        success = await chat_service.delete_session(session_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        return {
            "message": "会话删除成功",
            "session_id": session_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除会话错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/emotion-trends")
async def get_user_emotion_trends(user_id: str):
    """获取用户情感趋势"""
    try:
        trends = await chat_service.get_user_emotion_trends(user_id)
        if "error" in trends:
            raise HTTPException(status_code=404, detail=trends["error"])
        return trends
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取情感趋势错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/with-attachments", response_model=ChatResponse)
async def chat_with_attachments(
    message: str = Form(...),
    session_id: str = Form(None),
    user_id: str = Form(...),
    url_contents: str = Form(None),
    files: List[UploadFile] = File(default=[])
):
    """带附件的聊天接口（支持文件上传）"""
    try:
        # 处理文件附件
        file_contents = []
        if files:
            for file in files:
                if not file.filename or not is_allowed_file(file.filename):
                    raise HTTPException(status_code=400, detail=f"不支持的文件类型: {file.filename}")
                
                # 保存文件
                file_id = str(uuid.uuid4())
                file_extension = Path(file.filename).suffix
                file_path = UPLOAD_DIR / f"{file_id}{file_extension}"
                
                # 读取文件内容并检查大小
                file_content = await file.read()
                if len(file_content) > MAX_FILE_SIZE:
                    raise HTTPException(status_code=400, detail=f"文件过大: {file.filename}")
                
                # 写入文件
                with open(file_path, "wb") as buffer:
                    buffer.write(file_content)
                
                # 提取文件内容
                content = ""
                if file_extension.lower() == '.pdf':
                    content = extract_text_from_pdf(file_path)
                elif file_extension.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
                    content = extract_text_from_image(file_path)
                elif file_extension.lower() == '.txt':
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                
                file_contents.append({
                    "filename": file.filename,
                    "content": content,
                    "type": file.content_type
                })
        
        # 处理URL内容
        url_contents_list = []
        if url_contents:
            try:
                url_contents_list = json.loads(url_contents)
            except json.JSONDecodeError:
                pass
        
        # 构建增强的消息内容
        enhanced_message = message
        if file_contents:
            enhanced_message += "\n\n[附件内容]:\n"
            for file_content in file_contents:
                content_preview = file_content['content'][:500] if file_content['content'] else "[空内容]"
                enhanced_message += f"\n文件: {file_content['filename']}\n内容: {content_preview}...\n"
        
        if url_contents_list:
            enhanced_message += "\n\n[URL内容]:\n"
            for url_content in url_contents_list:
                content_preview = url_content.get('content', '')[:500]
                enhanced_message += f"\n链接: {url_content['url']}\n标题: {url_content['title']}\n内容: {content_preview}...\n"
        
        # 创建聊天请求
        chat_request = ChatRequest(
            message=enhanced_message,
            session_id=session_id,
            user_id=user_id
        )
        
        # 调用聊天服务
        response = await chat_service.chat(chat_request, use_memory_system=True)
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"带附件聊天接口错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/parse-url")
async def parse_url(data: dict):
    """URL解析接口"""
    try:
        url = data.get("url")
        if not url:
            raise HTTPException(status_code=400, detail="URL参数缺失")
        
        result = parse_url_content(url)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"URL解析接口错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

