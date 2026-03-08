from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json


@login_required
def build_resume(request):
    """Resume builder with live preview"""
    user = request.user
    profile = user.profile
    
    # Get resume data from session or initialize defaults
    resume_data = request.session.get('resume_data', {
        'fullName': user.get_full_name() or user.username,
        'email': user.email,
        'phone': '',
        'location': profile.location if profile else '',
        'summary': user.bio or '',
        'skills': user.skills if user.skills else [],
        'experience': [],
        'education': [],
        'certifications': [],
        'projects': []
    })
    
    context = {
        'resume_data': json.dumps(resume_data),
        'user': user,
        'profile': profile
    }
    
    return render(request, 'dashboard/build_resume.html', context)


@login_required
def save_resume(request):
    """Save resume data to session"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            request.session['resume_data'] = data
            request.session.modified = True
            return JsonResponse({'success': True, 'message': 'Resume saved successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)


@login_required
def preview_resume(request):
    """Generate resume preview"""
    resume_data = request.session.get('resume_data', {})
    return JsonResponse(resume_data)
