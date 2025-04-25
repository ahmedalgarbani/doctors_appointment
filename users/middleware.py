from django.shortcuts import redirect

class RoleBasedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            user_role = request.user.user_type

            # Define restricted routes and their allowed roles
            restricted_routes = {
                '/hospital/': ['hospital_manager', 'hospital_staff'],  # السماح لمدير المستشفى وموظفي المستشفى
                '/patients/': 'patient',
            }

            # Check if the requested path is a restricted route
            for restricted_path, allowed_role in restricted_routes.items():
                if request.path.startswith(restricted_path):
                    # If the user's role doesn't match, redirect to login
                    if isinstance(allowed_role, list):
                        # إذا كانت الأدوار المسموح بها قائمة
                        if user_role not in allowed_role:
                            return redirect('/')
                    else:
                        # إذا كان الدور المسموح به قيمة واحدة
                        if user_role != allowed_role:
                            return redirect('/')

        elif request.path.startswith('/hospital/') or request.path.startswith('/patients/'):

            return redirect('/users/login/')

        return self.get_response(request)
