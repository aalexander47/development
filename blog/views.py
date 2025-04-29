from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.http import JsonResponse
import json
from datetime import datetime
from .models import Blog, BlogMedia
from django.contrib.auth.models import User
from authenticator.decorators import has_permission
from user.utils import get_cached_user
from core.utils import compress_image
from uuid import uuid4

# Create your views here.
@has_permission("admin, developer")
def blogs_cms_view(request):
    user = get_cached_user(request, 'staff')
    if request.method == "POST" and "add_blogs" in request.POST:
        name = request.POST.get("name", "")
        blog = Blog(name=name, user=request.user)
        blog.save()
        if blog.id:
            messages.success(request, "Blogs added successfully.")
        else:
            messages.error(request, "Error occurred while adding Blogs.")
        return redirect('Blog:Dashboard') 
    
    if request.method == "POST" and "delete_blogs" in request.POST:
        id = request.POST.get("delete_blogs", None)
        if id is not None:
            action = Blog.objects.filter(id=id).delete()
            if action[0] == 1:
                messages.success(request, "Docs deleted successfully.")
            else:
                messages.error(request, "Error occurred while deleting blogs.")
        return redirect('blog:Dashboard') 
    
    if request.method == "POST" and "update_status" in request.POST:
        update_status = request.POST.get("update_status", None)
        if update_status is not None:
            id =update_status.split("-")[1]
            status = update_status.split("-")[0]
            if id is not None and status is not None:
                Blog.objects.filter(id=id).update(status=status)
                messages.success(request, "Article status updated successfully.")
            else:
                messages.error(request, "Error occurred while updating Article status.")
        else:
            messages.error(request, "Error occurred while updating Article status.")    
        return redirect('blog:Dashboard') 
    
    blogs = Blog.objects.all()
    data = {
        "user": user,
        "cp": 'blogs',
        "blogs": blogs
    }
    return render(request, 'blog/cms/pages/blog.html', data)


@has_permission('admin, developer')
def blogs_create_cms_view(request):
    user = get_cached_user(request, 'staff')
    if request.method == 'POST' and "create_blogs" in request.POST:
        print('create_blogs')
        # Create a new blog
        name = request.POST.get('name', "")
        url = request.POST.get('slug', "")
        thumbnail = request.POST.get('thumbnail', "")
        recommendation_title = request.POST.get('recommendation_title', "")
        short_description = request.POST.get('short_description', "")
        recommendation_thumbnail = request.POST.get('recommendation_thumbnail', "")
        # Check and set foreign keys
        previous_blog_id = request.POST.get('previous_blog_id')
        next_blog_id = request.POST.get('next_blog_id')
        recommendation_blog_id = request.POST.get('recommendation_blog_id')

        seo_data = {
            "meta_title": request.POST.get('meta_title', ''),
            "meta_description": request.POST.get('meta_description', ''),
            "meta_keywords": request.POST.get('meta_keywords', ''),
            "og_title": request.POST.get('og_title', ''),
            "og_description": request.POST.get('og_description', ''),
            "og_image_url": request.POST.get('og_image_url', ''),
            "twitter_title": request.POST.get('twitter_title', ''),
            "twitter_description": request.POST.get('twitter_description', ''),
            "twitter_image_url": request.POST.get('twitter_image_url', '')
        }
        
        content_data = {
            'heading': request.POST.get('name', ''),
            'content':[],
        }
        
        for i in range(len(request.POST.getlist('content_area_id', []))):
            content_data['content'].append({
                'id': request.POST.getlist('content_area_id', '')[i],
                'content': request.POST.getlist('content', '')[i] ,           
            })
        # Save the blog
        _blogs = Blog.objects.create(
            user=request.user,
            name=name,
            url=url,
            thumbnail=thumbnail,
            recommendation_title=recommendation_title,
            short_description=short_description,
            recommendation_thumbnail=recommendation_thumbnail,
            previous_blog_id=previous_blog_id,
            next_blog_id=next_blog_id,
            recommendation_blog_id=recommendation_blog_id,
            seo_data=seo_data,
            content_data=content_data
        )
        if _blogs is not None:
            messages.success(request, "Blog added successfully.")
        else:
            messages.error(request, "Error occurred while adding blogs.")
            blogs = {
                'name': name,
                'url': url,
                'thumbnail': thumbnail,
                'recommendation_title': recommendation_title,
                'short_description': short_description,
                'recommendation_thumbnail': recommendation_thumbnail,
                'previous_blog_id': previous_blog_id,
                'next_blog_id': next_blog_id,
                'recommendation_blog_id': recommendation_blog_id,
                'seo_data': seo_data,
                'content_data': content_data
            }
            context = {
                'cp': 'blogs',
                'action': 'create',
                'user': user,
                'blogs': blogs
            }
            return render(request, 'blog/cms/pages/blog_create.html', context)
        
        return redirect('blog:Dashboard')
    context = {
        'cp': 'blogs',
        'action': 'create',
        'user': user
    }
    return render(request, 'blog/cms/pages/blog_create.html', context)

@has_permission('admin, developer')
def blogs_update_cms_view(request, id):
    user = get_cached_user(request, 'staff')
    _blogs = Blog.objects.filter(id=id).first()
    if request.method == 'POST' and "update_blogs" in request.POST:
        name = request.POST.get('name', "")
        url = request.POST.get('slug', "")
        thumbnail = request.POST.get('thumbnail', "")
        recommendation_title = request.POST.get('recommendation_title', "")
        short_description = request.POST.get('short_description', "")
        recommendation_thumbnail = request.POST.get('recommendation_thumbnail', "")
        # Check and set foreign keys
        previous_blog_id = request.POST.get('previous_blog_id')
        next_blog_id = request.POST.get('next_blog_id')
        recommendation_blog_id = request.POST.get('recommendation_blog_id')

        seo_data = {
            "meta_title": request.POST.get('meta_title', ''),
            "meta_description": request.POST.get('meta_description', ''),
            "meta_keywords": request.POST.get('meta_keywords', ''),
            "og_title": request.POST.get('og_title', ''),
            "og_description": request.POST.get('og_description', ''),
            "og_image_url": request.POST.get('og_image_url', ''),
            "twitter_title": request.POST.get('twitter_title', ''),
            "twitter_description": request.POST.get('twitter_description', ''),
            "twitter_image_url": request.POST.get('twitter_image_url', '')
        }
        
        content_data = {
            'heading': request.POST.get('name', ''),
            'content':[],
        }
        
        for i in range(len(request.POST.getlist('content_area_id', []))):
            content_data['content'].append({
                'id': request.POST.getlist('content_area_id', '')[i],
                'content': request.POST.getlist('content', '')[i],           
            })
        # Save the blog
        _blogs = Blog.objects.filter(id=id).update(
            name=name,
            url=url,
            thumbnail=thumbnail,
            recommendation_title=recommendation_title,
            short_description=short_description,
            recommendation_thumbnail=recommendation_thumbnail,
            previous_blog_id=previous_blog_id,
            next_blog_id=next_blog_id,
            recommendation_blog_id=recommendation_blog_id,
            seo_data=seo_data,
            content_data=content_data
        )
        if _blogs is not None:
            messages.success(request, "Blog updated successfully.")
        else:
            messages.error(request, "Error occurred while updating blogs.")
            blogs = {
                'name': name,
                'url': url,
                'thumbnail': thumbnail,
                'recommendation_title': recommendation_title,
                'short_description': short_description,
                'recommendation_thumbnail': recommendation_thumbnail,
                'previous_blog_id': previous_blog_id,
                'next_blog_id': next_blog_id,
                'recommendation_blog_id': recommendation_blog_id,
                'seo_data': seo_data,
                'content_data': content_data
            }
            context = {
                'cp': 'blogs',
                'action': 'update',
                'user': user,
                'blogs': blogs
            }
            return render(request, 'blog/cms/pages/blog_create.html', context)
        
        return redirect(request.META.get('HTTP_REFERER', 'blog:Dashboard'))
    context = {
        'cp': 'blogs',
        'action': 'update',
        'user': user,
        'blogs': _blogs
    }
    return render(request, 'blog/cms/pages/blog_create.html', context)

@has_permission('admin, developer')
def blogs_delete_cms_view(request, id):
    user = get_cached_user(request, 'staff')
    _blogs = Blog.objects.filter(id=id, user=request.user).first()
    if _blogs is not None:
        _blogs.delete()
        messages.success(request, "Docs deleted successfully.")
    else:
        messages.error(request, "Error occurred while deleting blogs.")
    return redirect('blog:Dashboard')


@has_permission('admin, developer')
def media_cms_view(request):
    user = get_cached_user(request, 'staff')
    if request.method == 'POST' and 'add_media' in request.POST:
        # Retrieve files and descriptions once
        image_files = request.FILES.getlist('imageFile')
        image_descriptions = request.POST.getlist('imageDescription')

        if not image_files:
            messages.error(request, "Please select at least one image.")
            return redirect('blog:Media')

        # Prepare lists for bulk creation
        blogs_media_instances = []

        # Loop through images and prepare instances
        for i, image in enumerate(image_files):
            if image:
                description = image_descriptions[i] if i < len(image_descriptions) else ''
                
                # Compress image before saving
                # image = compress_image(image, quality=30)
                image.name = f"blogs-{str(uuid4())[:8]}.{image.name.split('.')[-1]}"
                
                # Create Media instance
                blogs_media = BlogMedia(
                    user=request.user,
                    image=image,
                    description=description
                )
                blogs_media_instances.append(blogs_media)

        if not blogs_media_instances:
            messages.error(request, "Error occurred while adding images.")
            return redirect('blog:Media')

        # Bulk create PhotographerGallery instances
        created_media = BlogMedia.objects.bulk_create(blogs_media_instances)
        if created_media:
            messages.success(request, "Images have been added successfully.")
        else:
            messages.error(request, "Error occurred while adding images.")

        return redirect('blog:Media')

    if request.method == 'POST' and 'delete_media' in request.POST:
        id = request.POST.get('delete_media', None)
        if id is not None:
            action = BlogMedia.objects.filter(id=id).delete()

            if action[0] == 1:
                messages.success(request, "Image deleted successfully.")
            else:
                messages.error(request, "Error occurred while deleting image.")
        return redirect('blog:Media')
    
    media = BlogMedia.objects.all()

    context = {
        'cp': 'media',
        'media': media,
        'user': user
    }
    return render(request, 'blog/cms/pages/media.html', context)

@has_permission('admin, developer')
def media_delete_cms_view(request, id):
    # delete image
    image = get_object_or_404(BlogMedia, id=id)
    image.delete()
    messages.success(request, "Image has been deleted successfully.")
    return redirect('blog:Media')


# Function for the '<str:blog_url>/' path
def blog_view(request, blog_url):
    blog = Blog.objects.filter(url=blog_url).first()
    if blog is None:
        messages.error(request, "Blog not found.")  # Add an error message if the blog is not found
        return redirect('blog:Docs')  # Redirect to the main blogs page
    context = {
        'blog': blog  # Pass the single blog object to the template
    }
    return render(request, 'blog/pages/blog.html', context)  # Ensure the correct template is used


@has_permission("admin, developer")
def search_view(request):
    return render(request, 'blog/pages/search.html')


@has_permission("admin, developer")
def sitemap_view(request):
    if request.method == "POST" and "add_url" in request.POST:
        location = request.POST.get('location', '')
        priority = request.POST.get('priority', '')
        lastmod = request.POST.get('lastmod', '')
        changefreq = "monthly"

        url_data = {
            "location": location,
            "priority": priority,
            "lastmod": lastmod,
            "changefreq": changefreq
        }

        # Save sitemap URL logic here

        return redirect('blog:Sitemap')  

    # Fetch sitemap URLs logic here

    data = {
        "sitemaps": []
    }
    return render(request, 'blog/pages/sitemap.html', data)

@login_required
def save_blog(request, blog_id):
    if request.method == 'POST':
        # Update basic fields
        blog = Blog.objects.get(id=blog_id)
        blog.name = request.POST.get('name', blog.name)
        blog.url = request.POST.get('url', blog.url)
        blog.thumbnail = request.POST.get('thumbnail', blog.thumbnail)
        blog.recommendation_title = request.POST.get('recommendation_title', blog.recommendation_title)
        blog.short_description = request.POST.get('short_description', blog.short_description)
        blog.recommendation_thumbnail = request.POST.get('recommendation_thumbnail', blog.recommendation_thumbnail)
        # Check and set foreign keys
        previous_blog_id = request.POST.get('previous_blog_id')
        next_blog_id = request.POST.get('next_blog_id')
        recommendation_blog_id = request.POST.get('recommendation_blog_id')
        blog.previous_blog = previous_blog_id
        blog.next_blog = next_blog_id
        blog.recommendation_blog = recommendation_blog_id
        seo_data = {
            "title": request.POST.get('head_title', ''),
            "description": request.POST.get('head_description', ''),
            "keywords": request.POST.get('head_keywords', ''),
            "canonical_url": request.POST.get('canonical_url', ''),
            "og_title": request.POST.get('og_title', ''),
            "og_description": request.POST.get('og_description', ''),
            "og_image": request.POST.get('head_image_url', ''),
            "twitter_title": request.POST.get('twitter_title', ''),
            "twitter_description": request.POST.get('twitter_description', ''),
            "twitter_image": request.POST.get('twitter_image', '')
        }
        
        content_data = {
            'heading': request.POST.get('blogsTitleInput', ''),
            'content':[],
        }
        for i in range(len(request.POST.getlist('content_area_id', []))):
            content_data['content'].append({
                'id': request.POST.getlist('content_area_id', '')[i],
                'cardType': request.POST.getlist('card_type','')[i],
                'content': request.POST.getlist('content', '')[i] ,           
            })
           
        # Update JSON fields
        blog.seo_data = seo_data
        blog.content_data = content_data
        # Save the blog
        blog.save()
        messages.success(request, "Article saved successfully.")
        return redirect('blog:Article', id=blog.id)
    return render(request, 'blog/pages/blog.html')


def blogs_view(request):
    blogs = Blog.objects.all()  # Ensure all blogs are retrieved
    context = {
        "blogs": blogs  # Pass blogs to the template
    }
    return render(request, 'blog/pages/home.html', context)  # Ensure the correct template is used