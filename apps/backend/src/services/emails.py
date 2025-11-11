"""Email service using AWS SES."""

import boto3
from botocore.exceptions import ClientError

from ..core.config import get_settings
from ..core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

ses_client = boto3.client('ses', region_name=settings.SES_REGION)


async def send_magic_link_email(email: str, magic_link: str, locale: str = "ar") -> bool:
    """
    Send magic link email via SES.
    
    Args:
        email: Recipient email address
        magic_link: Full verification URL
        locale: Language (ar or en)
    
    Returns:
        True if sent successfully, False otherwise
    """
    try:
        subject = "تسجيل الدخول إلى Pulse AI" if locale == "ar" else "Login to Pulse AI"
        
        body_ar = f"""
        مرحباً،
        
        انقر على الرابط أدناه لتسجيل الدخول إلى Pulse AI Studio:
        
        {magic_link}
        
        هذا الرابط صالح لمدة 10 دقائق.
        
        إذا لم تطلب هذا البريد، يمكنك تجاهله بأمان.
        
        مع تحياتنا،
        فريق Pulse AI
        """
        
        body_en = f"""
        Hello,
        
        Click the link below to login to Pulse AI Studio:
        
        {magic_link}
        
        This link expires in 10 minutes.
        
        If you didn't request this email, you can safely ignore it.
        
        Best regards,
        Pulse AI Team
        """
        
        body = body_ar if locale == "ar" else body_en
        
        response = ses_client.send_email(
            Source=settings.EMAIL_FROM,
            Destination={'ToAddresses': [email]},
            Message={
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {
                    'Text': {'Data': body, 'Charset': 'UTF-8'}
                }
            }
        )
        
        logger.info(f"Magic link email sent: email={email}, message_id={response['MessageId']}")
        return True
        
    except ClientError as e:
        logger.error(f"Failed to send magic link email: {str(e)}")
        return False

