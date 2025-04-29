from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.http import JsonResponse
import json
from datetime import datetime
from .models import DocsArticle, ArticlesMedia
from django.contrib.auth.models import User
from authenticator.decorators import has_permission
from user.utils import get_cached_user
from core.utils import compress_image
from uuid import uuid4

# Create your views here.
@has_permission("admin, developer")
def docs_cms_view(request):
    user = get_cached_user(request, 'staff')
    if request.method == "POST" and "add_docs" in request.POST:
        name = request.POST.get("name", "")
        article = DocsArticle(name=name, user=request.user)
        article.save()
        if article.id:
            messages.success(request, "Docs added successfully.")
        else:
            messages.error(request, "Error occurred while adding docs.")
        return redirect('docs:Dashboard') 
    
    if request.method == "POST" and "delete_docs" in request.POST:
        id = request.POST.get("delete_docs", None)
        if id is not None:
            action = DocsArticle.objects.filter(id=id).delete()
            if action[0] == 1:
                messages.success(request, "Docs deleted successfully.")
            else:
                messages.error(request, "Error occurred while deleting docs.")
        return redirect('docs:Dashboard') 
    
    if request.method == "POST" and "update_status" in request.POST:
        update_status = request.POST.get("update_status", None)
        if update_status is not None:
            id =update_status.split("-")[1]
            status = update_status.split("-")[0]
            if id is not None and status is not None:
                DocsArticle.objects.filter(id=id).update(status=status)
                messages.success(request, "Article status updated successfully.")
            else:
                messages.error(request, "Error occurred while updating Article status.")
        else:
            messages.error(request, "Error occurred while updating Article status.")    
        return redirect('docs:Dashboard') 
    
    docs = DocsArticle.objects.all()
    data = {
        "user": user,
        "cp": 'docs',
        "docs": docs
    }
    return render(request, 'docs/cms/pages/docs.html', data)


@has_permission('admin, developer')
def docs_create_cms_view(request):
    user = get_cached_user(request, 'staff')
    if request.method == 'POST' and "create_docs" in request.POST:
        print('create_docs')
        # Create a new article
        name = request.POST.get('name', "")
        url = request.POST.get('slug', "")
        thumbnail = request.POST.get('thumbnail', "")
        recommendation_title = request.POST.get('recommendation_title', "")
        short_description = request.POST.get('short_description', "")
        recommendation_thumbnail = request.POST.get('recommendation_thumbnail', "")
        # Check and set foreign keys
        previous_article_id = request.POST.get('previous_article_id')
        next_article_id = request.POST.get('next_article_id')
        recommendation_article_id = request.POST.get('recommendation_article_id')

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
        # Save the article
        _docs = DocsArticle.objects.create(
            user=request.user,
            name=name,
            url=url,
            thumbnail=thumbnail,
            recommendation_title=recommendation_title,
            short_description=short_description,
            recommendation_thumbnail=recommendation_thumbnail,
            previous_article_id=previous_article_id,
            next_article_id=next_article_id,
            recommendation_article_id=recommendation_article_id,
            seo_data=seo_data,
            content_data=content_data
        )
        if _docs is not None:
            messages.success(request, "Docs added successfully.")
        else:
            messages.error(request, "Error occurred while adding docs.")
            docs = {
                'name': name,
                'url': url,
                'thumbnail': thumbnail,
                'recommendation_title': recommendation_title,
                'short_description': short_description,
                'recommendation_thumbnail': recommendation_thumbnail,
                'previous_article_id': previous_article_id,
                'next_article_id': next_article_id,
                'recommendation_article_id': recommendation_article_id,
                'seo_data': seo_data,
                'content_data': content_data
            }
            context = {
                'cp': 'docs',
                'action': 'create',
                'user': user,
                'docs': docs
            }
            return render(request, 'docs/cms/pages/docs_create.html', context)
        
        return redirect('docs:Dashboard')
    context = {
        'cp': 'docs',
        'action': 'create',
        'user': user
    }
    return render(request, 'docs/cms/pages/docs_create.html', context)

@has_permission('admin, developer')
def docs_update_cms_view(request, id):
    user = get_cached_user(request, 'staff')
    _docs = DocsArticle.objects.filter(id=id).first()
    if request.method == 'POST' and "update_docs" in request.POST:
        name = request.POST.get('name', "")
        url = request.POST.get('slug', "")
        thumbnail = request.POST.get('thumbnail', "")
        recommendation_title = request.POST.get('recommendation_title', "")
        short_description = request.POST.get('short_description', "")
        recommendation_thumbnail = request.POST.get('recommendation_thumbnail', "")
        # Check and set foreign keys
        previous_article_id = request.POST.get('previous_article_id')
        next_article_id = request.POST.get('next_article_id')
        recommendation_article_id = request.POST.get('recommendation_article_id')

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
        # Save the article
        _docs = DocsArticle.objects.filter(id=id).update(
            name=name,
            url=url,
            thumbnail=thumbnail,
            recommendation_title=recommendation_title,
            short_description=short_description,
            recommendation_thumbnail=recommendation_thumbnail,
            previous_article_id=previous_article_id,
            next_article_id=next_article_id,
            recommendation_article_id=recommendation_article_id,
            seo_data=seo_data,
            content_data=content_data
        )
        if _docs is not None:
            messages.success(request, "Docs updated successfully.")
        else:
            messages.error(request, "Error occurred while updating docs.")
            docs = {
                'name': name,
                'url': url,
                'thumbnail': thumbnail,
                'recommendation_title': recommendation_title,
                'short_description': short_description,
                'recommendation_thumbnail': recommendation_thumbnail,
                'previous_article_id': previous_article_id,
                'next_article_id': next_article_id,
                'recommendation_article_id': recommendation_article_id,
                'seo_data': seo_data,
                'content_data': content_data
            }
            context = {
                'cp': 'docs',
                'action': 'update',
                'user': user,
                'docs': docs
            }
            return render(request, 'docs/cms/pages/docs_create.html', context)
        
        return redirect(request.META.get('HTTP_REFERER', 'docs:Dashboard'))
    context = {
        'cp': 'docs',
        'action': 'update',
        'user': user,
        'docs': _docs
    }
    return render(request, 'docs/cms/pages/docs_create.html', context)

@has_permission('admin, developer')
def docs_delete_cms_view(request, id):
    user = get_cached_user(request, 'staff')
    _docs = DocsArticle.objects.filter(id=id, user=request.user).first()
    if _docs is not None:
        _docs.delete()
        messages.success(request, "Docs deleted successfully.")
    else:
        messages.error(request, "Error occurred while deleting docs.")
    return redirect('docs:Dashboard')

@has_permission('admin, developer')
def articles_cms_view(request):
    user = get_cached_user(request, 'staff')
    context = {
        'cp': 'articles',
        'user': user
    }
    return render(request, 'docs/cms/pages/articles.html', context)

@has_permission('admin, developer')
def media_cms_view(request):
    user = get_cached_user(request, 'staff')
    if request.method == 'POST' and 'add_media' in request.POST:
        # Retrieve files and descriptions once
        image_files = request.FILES.getlist('imageFile')
        image_descriptions = request.POST.getlist('imageDescription')

        if not image_files:
            messages.error(request, "Please select at least one image.")
            return redirect('docs:Media')

        # Prepare lists for bulk creation
        docs_media_instances = []

        # Loop through images and prepare instances
        for i, image in enumerate(image_files):
            if image:
                description = image_descriptions[i] if i < len(image_descriptions) else ''
                
                # Compress image before saving
                # image = compress_image(image, quality=30)
                image.name = f"docs-{str(uuid4())[:8]}.{image.name.split('.')[-1]}"
                
                # Create Media instance
                docs_media = ArticlesMedia(
                    user=request.user,
                    image=image,
                    description=description
                )
                docs_media_instances.append(docs_media)

        if not docs_media_instances:
            messages.error(request, "Error occurred while adding images.")
            return redirect('docs:Media')

        # Bulk create PhotographerGallery instances
        created_media = ArticlesMedia.objects.bulk_create(docs_media_instances)
        if created_media:
            messages.success(request, "Images have been added successfully.")
        else:
            messages.error(request, "Error occurred while adding images.")

        return redirect('docs:Media')

    if request.method == 'POST' and 'delete_media' in request.POST:
        id = request.POST.get('delete_media', None)
        if id is not None:
            action = ArticlesMedia.objects.filter(id=id).delete()

            if action[0] == 1:
                messages.success(request, "Image deleted successfully.")
            else:
                messages.error(request, "Error occurred while deleting image.")
        return redirect('docs:Media')
    
    media = ArticlesMedia.objects.all()

    context = {
        'cp': 'media',
        'media': media,
        'user': user
    }
    return render(request, 'docs/cms/pages/media.html', context)

@has_permission('admin, developer')
def media_delete_cms_view(request, id):
    # delete image
    image = get_object_or_404(ArticlesMedia, id=id)
    image.delete()
    messages.success(request, "Image has been deleted successfully.")
    return redirect('docs:Media')


def doc_view(request, doc_url):
    doc = DocsArticle.objects.filter(url=doc_url).first()
    if doc is None:
        return redirect('docs:Dashboard')
    context = {
        'docs': doc
    }
    return render(request, 'docs/pages/docs.html', context)


@has_permission("admin, developer")
def search_view(request):
    return render(request, 'docs/pages/search.html')


@has_permission("admin, developer")
def article_view(request, id):
    if request.method == "POST" and "update" in request.POST:
        data_block = {
            'name': request.POST.get('name'),
            'url': request.POST.get('url'),
            'thumbnail': request.POST.get('thumbnail'),
            'recommendation_title': request.POST.get('recommendation_title'),
            'short_description': request.POST.get('short_description'),
            'recommendation_thumbnail': request.POST.get('recommendation_thumbnail'),
            'previous_article_id': request.POST.get('previous_article_id'),
            'next_article_id': request.POST.get('next_article_id'),
            'recommendation_article_id': request.POST.get('recommendation_article_id'),
            'seo_data': json.loads(request.POST.get('seo_data')),
            'content_data': json.loads(request.POST.get('content_data'))
        }       
        # Remove any keys with None values
        data_block = {k: v for k, v in data_block.items() if v is not None}
        DocsArticle.objects.filter(id=id).update(**data_block)
        messages.success(request, "Article updated successfully.")
        return redirect('docs:Article', id=id)
    insurance_data = DocsArticle.objects.get(id=id)
    data = {
        "insurance": insurance_data,
        "recommendation_title": insurance_data.recommendation_title,
        "short_description": insurance_data.short_description,
        "recommendation_thumbnail": insurance_data.recommendation_thumbnail,
        "previous_article_id": insurance_data.previous_article_id if insurance_data.previous_article_id else '',
        "next_article_id": insurance_data.next_article_id if insurance_data.next_article_id else '',
        "recommendation_article_id": insurance_data.recommendation_article_id if insurance_data.recommendation_article_id else '',
        "seo_data": insurance_data.seo_data,
        "content_data": insurance_data.content_data
    }
    return render(request, 'docs/pages/article.html', data)


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

        return redirect('docs:Sitemap')  

    # Fetch sitemap URLs logic here

    data = {
        "sitemaps": []
    }
    return render(request, 'docs/pages/sitemap.html', data)

@login_required
def save_article(request, article_id):
    if request.method == 'POST':
        # Update basic fields
        article = DocsArticle.objects.get(id=article_id)
        article.name = request.POST.get('name', article.name)
        article.url = request.POST.get('url', article.url)
        article.thumbnail = request.POST.get('thumbnail', article.thumbnail)
        article.recommendation_title = request.POST.get('recommendation_title', article.recommendation_title)
        article.short_description = request.POST.get('short_description', article.short_description)
        article.recommendation_thumbnail = request.POST.get('recommendation_thumbnail', article.recommendation_thumbnail)
        # Check and set foreign keys
        previous_article_id = request.POST.get('previous_article_id')
        next_article_id = request.POST.get('next_article_id')
        recommendation_article_id = request.POST.get('recommendation_article_id')
        article.previous_article = previous_article_id
        article.next_article = next_article_id
        article.recommendation_article = recommendation_article_id
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
            'heading': request.POST.get('docsTitleInput', ''),
            'content':[],
        }
        for i in range(len(request.POST.getlist('content_area_id', []))):
            content_data['content'].append({
                'id': request.POST.getlist('content_area_id', '')[i],
                'cardType': request.POST.getlist('card_type','')[i],
                'content': request.POST.getlist('content', '')[i] ,           
            })
           
        # Update JSON fields
        article.seo_data = seo_data
        article.content_data = content_data
        # Save the article
        article.save()
        messages.success(request, "Article saved successfully.")
        return redirect('docs:Article', id=article.id)
    return render(request, 'docs/pages/article.html')


def docs_view(request):
    docs = DocsArticle.objects.all()
    data = {
        "docs": docs
    }
    return render(request, 'docs/pages/home.html', data)