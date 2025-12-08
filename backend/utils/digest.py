"""
Email digest generation and delivery.
"""
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


def send_digest_to_user(user, events, digest_type='08:00'):
    """
    Send digest email to user.
    
    Args:
        user: User object
        events: List of Event objects
        digest_type: '08:00' or '15:00'
        
    Returns:
        bool: True if sent successfully
    """
    try:
        html_content = generate_digest_html(events, digest_type, user)
        text_content = generate_digest_text(events, digest_type, user)
        
        subject = f"Your {digest_type} Event Digest"
        if digest_type == '15:00':
            subject = "Today's Events - Last Call"
        
        return send_email(
            to_email=user.email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
    except Exception as e:
        print(f"Error sending digest: {e}")
        return False


def generate_digest_html(events, digest_type, user):
    """Generate HTML email content"""
    
    if not events:
        empty_message = "No upcoming events" if digest_type == '08:00' \
            else "No more events today"
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>Your {digest_type} Digest</h2>
                <p>{empty_message}. Enjoy your day!</p>
            </body>
        </html>
        """
    
    events_html = ""
    for event in events:
        tag_color = get_tag_color(event.tag)
        
        events_html += f"""
        <div style="border-left: 4px solid {tag_color}; padding: 15px;
                    margin: 15px 0; background: #f9f9f9;">
            <h3 style="margin: 0 0 10px 0;">{event.title}</h3>
            <p style="margin: 5px 0; color: #666;">
                <strong>Time:</strong>
                {event.start_time.strftime('%I:%M %p on %B %d, %Y')}
            </p>
            {f'<p style="margin: 5px 0; color: #666;"><strong>Location:</strong> {event.location}</p>' if event.location else ''}
            {f'<p style="margin: 5px 0; color: #666;"><strong>Meeting Link:</strong> <a href="{event.meeting_link}">{event.meeting_link}</a></p>' if event.meeting_link else ''}
            <p style="margin: 5px 0;">
                <span style="background: {tag_color}; color: white;
                            padding: 3px 8px; border-radius: 3px;
                            font-size: 12px;">
                    {event.tag}
                </span>
                <span style="color: #888; margin-left: 10px; font-size: 12px;">
                    via {event.source.name}
                </span>
            </p>
            {f'<p style="margin: 10px 0; font-style: italic;">{event.why_matters}</p>' if event.why_matters else ''}
            {f'<p style="margin: 10px 0;"><a href="{event.rsvp_link}" style="color: #007bff;">RSVP →</a></p>' if event.rsvp_link else ''}
            {f'<p style="margin: 10px 0; color: #555;">{event.description}</p>' if event.description else ''}
        </div>
        """
    
    return f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px;
                     margin: 0 auto;">
            <h2>Your {digest_type} Digest</h2>
            <p>Hi {user.name or 'there'}! Here are your upcoming events:</p>
            {events_html}
            <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
            <p style="color: #888; font-size: 12px;">
                You're receiving this because you subscribed to Concierge digests.
            </p>
        </body>
    </html>
    """


def generate_digest_text(events, digest_type, user):
    """Generate plain text email content"""
    
    if not events:
        empty_message = "No upcoming events" if digest_type == '08:00' \
            else "No more events today"
        return f"Your {digest_type} Digest\n\n{empty_message}. Enjoy!"
    
    text = f"Your {digest_type} Digest\n\n"
    text += f"Hi {user.name or 'there'}! Here are your upcoming events:\n\n"
    text += "=" * 60 + "\n\n"
    
    for event in events:
        text += f"{event.title}\n"
        text += f"Time: {event.start_time.strftime('%I:%M %p on %B %d, %Y')}\n"
        
        if event.location:
            text += f"Location: {event.location}\n"
        if event.meeting_link:
            text += f"Meeting: {event.meeting_link}\n"
        
        text += f"Tag: {event.tag} | Source: {event.source.name}\n"
        
        if event.why_matters:
            text += f"\n{event.why_matters}\n"
        if event.rsvp_link:
            text += f"RSVP: {event.rsvp_link}\n"
        
        text += "\n" + "-" * 60 + "\n\n"
    
    return text


def get_tag_color(tag):
    """Get color for event tag"""
    colors = {
        'Required': '#dc3545',
        'Career': '#28a745',
        'Capstone': '#007bff',
        'Social': '#ffc107',
        'Deadline': '#fd7e14'
    }
    return colors.get(tag, '#6c757d')


def send_email(to_email, subject, html_content, text_content):
    """
    Send email via SMTP.
    
    Returns:
        bool: True if sent successfully
    """
    smtp_host = os.getenv('SMTP_HOST')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    from_email = os.getenv('FROM_EMAIL', smtp_user)
    
    # Skip if SMTP not configured
    if not all([smtp_host, smtp_user, smtp_password]):
        print("SMTP not configured, skipping email send")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email
        
        # Attach both plain text and HTML
        part1 = MIMEText(text_content, 'plain')
        part2 = MIMEText(html_content, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Send via SMTP
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        return True
        
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
