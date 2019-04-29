import datetime
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone
from django.core.cache import cache
from blog.models import Blog
from blog.utils import get_seven_days_read_data, get_today_hot_data, get_yesterday_hot_data


def get_7_days_hot_data():
    today = timezone.now().date()
    date = today - datetime.timedelta(days=7)
    # 根据object_id分组求和
    blogs = Blog.objects\
                 .filter(read_details__date__lt=today, read_details__date__gte=date)\
                 .values('id', 'title')\
                 .annotate(read_num_sum=Sum('read_details__read_num'))\
                 .order_by('-read_num_sum')
    return blogs[:7]


def get_30_days_hot_data():
    today = timezone.now().date()
    date = today - datetime.timedelta(days=30)
    # 根据object_id分组求和
    blogs = Blog.objects\
                 .filter(read_details__date__lt=today, read_details__date__gte=date)\
                 .values('id', 'title')\
                 .annotate(read_num_sum=Sum('read_details__read_num'))\
                 .order_by('-read_num_sum')
    return blogs[:7]


def home(request):
    blog_content_type = ContentType.objects.get_for_model(Blog)
    dates, read_nums = get_seven_days_read_data(blog_content_type)
    seven_days_hot_data = cache.get('7_days_hot_data')
    if seven_days_hot_data is None:
        seven_days_hot_data = get_7_days_hot_data()
        cache.set('7_days_hot_data', seven_days_hot_data, 3600)  # 有效期1小时

    one_month_hot_data = cache.get('30_days_hot_data')
    if one_month_hot_data is None:
        one_month_hot_data = get_30_days_hot_data()
        cache.set('30_days_hot_data', one_month_hot_data, 3600)  # 有效期1小时

    context = {
        'read_nums': read_nums,
        'dates': dates,
        'today_hot_data': get_today_hot_data(blog_content_type),
        'yesterday_hot_data': get_yesterday_hot_data(blog_content_type),
        '7_days_hot_data': seven_days_hot_data,
        '30_days_hot_data': one_month_hot_data,
    }
    return render(request, 'home.html', context)

