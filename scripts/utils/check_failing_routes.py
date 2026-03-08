from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model

from apps.jobs.views_public import job_detail
from apps.social.views_public import user_profile


def check_view(label, func, path, **kwargs):
    rf = RequestFactory()
    req = rf.get(path, HTTP_HOST='127.0.0.1')
    req.user = AnonymousUser()
    try:
        resp = func(req, **kwargs)
        print(f"OK {label}: {resp.status_code}")
    except Exception as exc:
        print(f"ERR {label}: {type(exc).__name__}: {exc}")
        import traceback

        traceback.print_exc()


def main():
    User = get_user_model()
    sample_user = User.objects.order_by('id').first()
    sample_user_id = sample_user.id if sample_user else 1

    check_view('jobs.detail', job_detail, '/jobs/1/', pk=1)
    check_view('social.profile', user_profile, f'/community/profile/{sample_user_id}/', user_id=sample_user_id)


if __name__ == '__main__':
    main()
