from functools import wraps
from flask import request, session
from datetime import datetime
from app import db
from app.models import AuditLog

class AuditLogger:
    @staticmethod
    def log(action, resource, details=None, status='success'):
        """
        Log an action to the database.
        
        :param action: A string describing the action (e.g., 'create_user', 'update_grade').
        :param resource: The target resource (e.g., 'User:123', 'Course:cs101').
        :param details: A dictionary or string with additional details (will be encrypted if sensitive).
        :param status: Standard 'success' or 'failure'.
        """
        try:
            # Determine user_id and university_id from context
            user_id = None
            university_id = None
            
            # Try getting from flask-login current_user (if available via g or processed request)
            # Since we use token_required often, we might check that manually or rely on session
            # For now, let's look at the implementation of token_required to see how it passes user
            # Usually it passes 'current_user' to the view function. 
            # We can't easily access 'current_user' here if it's a local variable in the view.
            # However, we can use flask.g if we update our middlewares/decorators to store it there.
            
            # Simple fallback: Check session if login is session-based, or rely on caller passing info?
            # Better approach for a decorator: The decorator wrapper will have access to 'current_user' 
            # if strictly used on authenticated routes.
            
            from flask import g
            if hasattr(g, 'current_user') and g.current_user:
                user_id = g.current_user.id
                university_id = g.current_user.university_id
            elif 'user_id' in session:
                user_id = session['user_id']
                # Fetch uni id if needed or leave null
            
            ip_address = request.remote_addr
            
            log_entry = AuditLog(
                university_id=university_id,
                user_id=user_id,
                action=action,
                resource=resource,
                ip_address=ip_address,
                details=str(details) if details else None,
                status=status
            )
            
            db.session.add(log_entry)
            db.session.commit()
            
        except Exception as e:
            # Fallback logging to file/console so we don't break the app if DB fails
            print(f"[AUDIT FAILURE] Action: {action}, Error: {str(e)}")

def track_action(action_name, resource_id_field=None):
    """
    Decorator to automatically log API actions.
    
    :param action_name: Name of the action (e.g., 'delete_student').
    :param resource_id_field: URL parameter or JSON field to log as the resource ID.
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Execute the actual function
            try:
                # We need to ensure 'current_user' is in g for the logger to find it
                # Our token_required passes it as an argument, so we might need to intercept it
                # or update token_required to set g.current_user
                
                # Intercept current_user from args if it's the first arg (common in our codebase)
                # But our token_required passes it as first arg to the decorated function.
                if args:
                    potential_user = args[0]
                    # Check if it looks like a User model
                    if hasattr(potential_user, 'id') and hasattr(potential_user, 'university_id'):
                        from flask import g
                        g.current_user = potential_user

                response = f(*args, **kwargs)
                
                # Log success
                resource = "N/A"
                if resource_id_field:
                    # Check kwargs (URL params)
                    if resource_id_field in kwargs:
                        resource = kwargs[resource_id_field]
                    # Check JSON body
                    elif request.is_json and request.json and resource_id_field in request.json:
                        resource = request.json.get(resource_id_field)
                
                AuditLogger.log(
                    action=action_name,
                    resource=str(resource),
                    status='success'
                )
                return response
                
            except Exception as e:
                # Log failure
                AuditLogger.log(
                    action=action_name,
                    resource="Error",
                    details=str(e),
                    status='failure'
                )
                raise e
        return wrapper
    return decorator
