from django import forms
from django.db import models

# Add these:
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase
from wagtail.models import Page, Orderable, PreviewableMixin
from wagtail.fields import RichTextField, StreamField
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel, TabbedInterface, ObjectList
from wagtail.search import index
from wagtail.snippets.models import register_snippet
from wagtail.images.blocks import ImageChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from .amp_utils import PageAMPTemplateMixin

class BlogIndexPage(Page):
    intro = RichTextField(blank=True)
    
    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron
        context = super().get_context(request)
        blogpages = self.get_children().live().order_by('-first_published_at')
        context['blogpages'] = blogpages
        return context

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ]
    
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        # Add extra variables and return the updated context
        context['blog_entries'] = BlogPage.objects.child_of(self).live()
        return context

class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'BlogPage',
        related_name='tagged_items',
        on_delete=models.CASCADE
    )
    
class PersonBlock(blocks.StructBlock):
    first_name = blocks.CharBlock()
    surname = blocks.CharBlock()
    photo = ImageChooserBlock(required=False)
    biography = blocks.RichTextBlock()
    
    class Meta:
        template = 'blog/templates/blog/person.html'
        icon = 'user'

class CommonContentBlock(blocks.StreamBlock):
    heading = blocks.CharBlock(form_classname="title")
    paragraph = blocks.RichTextBlock()
    image = ImageChooserBlock()
    
    class Meta:
        block_counts = {
            'heading': {'min_num': 1, 'max_num': 3},
        }
    
class BlogPage(PageAMPTemplateMixin, Page):
    page_description = "Use this page for converting users"
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    body = StreamField([
        ('person', PersonBlock()),
        ('gallery', blocks.ListBlock(ImageChooserBlock())),
        ('carousel', blocks.StreamBlock([
            ('image', ImageChooserBlock()),
            ('video', EmbedBlock()),
        ], icon='image')),
        ('common_content', CommonContentBlock()),
    ], min_num=2, max_num=7, use_json_field=True)
    authors = ParentalManyToManyField('blog.Author', blank=True)
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    feed_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    
    
    def main_image(self):
        gallery_item = self.gallery_images.first()
        if gallery_item:
            return gallery_item.image
        else:
            return None

    # Search index configuration
    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.FilterField('date'),
        #index.SearchField('body'),
    ]
    
    # Editor panels configuration

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('date'),
            FieldPanel('authors', widget=forms.CheckboxSelectMultiple),
            FieldPanel('tags'),
        ], heading="Blog information"),
        FieldPanel('intro'),
        FieldPanel('body'),
        InlinePanel('gallery_images', label="Gallery images"),
    ]
    
    sidebar_content_panels = [
        #FieldPanel('advert'),
        InlinePanel('related_links', heading="Related links", label="Related link"),
    ]
    
    promote_panels = [
        MultiFieldPanel(Page.promote_panels, "Common page configuration"),
        FieldPanel('feed_image'),
    ]
    
    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(sidebar_content_panels, heading='Sidebar content'),
        ObjectList(Page.promote_panels, heading='Promote'),
    ])
    # Parent page / subpage type rules

    parent_page_types = ['blog.BlogIndexPage']
    subpage_types = []
    
    #ajax_template = 'other_template_fragment.html'
    #template = 'other_template.html'
    #amp_template = 'my_custom_amp_template.html'
    

class BlogPageRelatedLink(Orderable):
    page = ParentalKey(BlogPage, on_delete=models.CASCADE, related_name='related_links')
    name = models.CharField(max_length=255)
    url = models.URLField()

    panels = [
        FieldPanel('name'),
        FieldPanel('url'),
    ]
#class Advert(PreviewableMixin, models.Model):
#    url = models.URLField(null=True, blank=True)
#    text = models.CharField(max_length=255)

#    panels = [
#        FieldPanel('url'),
#        FieldPanel('text'),
#    ]
#    search_fields = [
#        index.SearchField('text'),
#        index.AutocompleteField('text'),
#   ]

#   def get_preview_template(self, request, mode_name):
#        return "blog/templates/blog/advert.html"
    
class BlogPageGalleryImage(Orderable):
    page = ParentalKey(BlogPage, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
    caption = models.CharField(blank=True, max_length=250)

    panels = [
        FieldPanel('image'),
        FieldPanel('caption'),
    ]

@register_snippet
class Author(models.Model):
    name = models.CharField(max_length=255)
    author_image = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+'
    )

    panels = [
        FieldPanel('name'),
        FieldPanel('author_image'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Authors'

class BlogTagIndexPage(Page):

    def get_context(self, request):

        # Filter by tag
        tag = request.GET.get('tag')
        blogpages = BlogPage.objects.filter(tags__name=tag)

        # Update template context
        context = super().get_context(request)
        context['blogpages'] = blogpages
        return context

