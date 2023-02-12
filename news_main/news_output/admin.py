from django.contrib import admin
from django.db.models import F
from .models import *


from .forms import *

# class RubricInline(admin.StackedInline):
#     model = Rubric
#     search_fields = ('name',)
#
#     def get_extra(self, request, obj=None, **kwargs):
#         if obj:
#             return 3
#         else:
#             return 10
class RubricAdmin(admin.ModelAdmin):
    search_fields = ('name',)

# class NewsAdmin(admin.ModelAdmin):
#     list_display = ('title', 'description', 'published', 'file_path')
    # fields = ('title', 'description', 'published', 'file_path')

# class NewsAdmin(admin.ModelAdmin):
#     list_display = ('title', 'description', 'published', 'file_path')
#
#     list_display_links = ('title', 'description')
#     search_fields = ('title', 'description')
#     list_filter = ()
#     preserve_filters = False
#     date_hierarchy = 'published'
#     readonly_fields = ('published',)
    # actions = ('discount',)
    #
    # def discount(self, request, queryset):
    #     f = F('title')
    #     for rec in queryset:
    #         rec.price = f / 2
    #         rec.save()
    #     self.message_user(request, 'mission complete')
    #
    # discount.short_description = 'Уменьшить цену вдвое'

    # def get_fieldsets(self, request, obj=None):
    #     fieldsets = (
    #         (None, {
    #             'fields': ('title', 'description', 'rubric'),
    #             'classes': ('wide',),
    #         }),
    #         ('Дополнительные сведения', {
    #             'fields': ('file_path',),
    #             'description': 'Параметры, необязательные для указания.',
    #         }),
    #         ('Автоматически присваиваемое поля', {
    #             'fields': ('published',),
    #
    #         })
    #     )
    #     return fieldsets
    # autocomplete_fields = ('rubric',)
    # raw_id_fields = ('rubric',)
    # def view_on_site(self, rec):
    #     return reverse('news_output:detail', kwargs={'pk': rec.pk})

class SubRubricInline(admin.TabularInline):
    model = SubRubric

class SuperRubricAdmin(admin.ModelAdmin):
    exclude = ('super_rubric',)
    inlines = (SubRubricInline,)

class SubRubricAdmin(admin.ModelAdmin):
    form = SubRubricForm

class AdditionalImageInline(admin.TabularInline):
    model = AdditionalImage

class NewsAdmin(admin.ModelAdmin):
    list_display = ('rubric', 'title', 'description', 'author', 'image', 'published')
    list_display_links = ('title', 'description')
    fields = (('rubric', 'author'), 'title', 'description', 'image',)
    inlines = (AdditionalImageInline,)
    readonly_fields = ('published',)

    # def get_fieldsets(self, request, obj=None):
    #     fieldsets = (
    #         (None, {'fields': ('title', 'description', 'rubric'), 'classes': ('wide',),}),
    #         ('Дополнительные сведения', {'fields': ('file_path',),
    #          'description': 'Параметры, необязательные для указания.',}),
    #         ('Автоматически присваиваемое поля', {
    #          'fields': ('published',), }))
    #     return fieldsets
   # autocomplete_fields = ('rubric',)

# class CommentAdmin(admin.ModelAdmin):
#     list_display = ('news', 'author', 'content', 'is_active', 'created_at')
#     list_display_links = ('news', 'author',)
#     fields = (('news', 'author',), 'content', 'is_active', 'created_at',)
#     readonly_fields = ('created_at',)

# class CommentUserInline(admin.TabularInline):
#     model = CommentUser
#     exclude = ('main_comment',)

class CommentPublicationAdmin(admin.ModelAdmin):
    exclude = ('target_comment', 'main_comment',)
    # inlines = (CommentUserInline,)

class CommentUserAdmin(admin.ModelAdmin):
    form = CommentUserForm

class LikeDislikeAdmin(admin.ModelAdmin):
    form = LikeDislikeForm

admin.site.register(Rubric,  RubricAdmin)
admin.site.register(SubRubric, SubRubricAdmin)
admin.site.register(SuperRubric, SuperRubricAdmin)
admin.site.register(News, NewsAdmin)
admin.site.register(CommentPublication, CommentPublicationAdmin)
admin.site.register(CommentUser, CommentUserAdmin)
admin.site.register(LikeDislike, LikeDislikeAdmin)


