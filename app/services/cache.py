from flask_caching import Cache
from flask import request, g

# Configure SimpleCache for development/single-server
# In production, use Redis by changing CACHE_TYPE to 'redis'
cache = Cache(config={'CACHE_TYPE': 'SimpleCache', 'CACHE_DEFAULT_TIMEOUT': 300})

def make_cache_key(*args, **kwargs):
    """
    Generate a dynamic cache key that includes the university context and user session.
    This ensures that one user doesn't see another's cached data.
    """
    path = request.path
    args_str = str(sorted(request.args.items()))
    from flask import session
    
    # Include university ID in the key if available (from tenant_required)
    uni_prefix = "global"
    if hasattr(g, 'current_tenant') and g.current_tenant:
        uni_prefix = f"uni_{g.current_tenant.id}"
    elif hasattr(g, 'current_user') and g.current_user and g.current_user.university_id:
        uni_prefix = f"uni_{g.current_user.university_id}"
    elif session.get('user_id'):
        uni_prefix = f"user_{session['user_id']}"
        
    return f"{uni_prefix}:{path}:{args_str}"
