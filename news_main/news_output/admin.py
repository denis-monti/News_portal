from django.contrib import admin
from django.db.models import F
from .models import *

<<<<<<< HEAD
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

class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'published', 'file_path')
    # fields = ('title', 'description', 'published', 'file_path')
=======
class Newsadmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'published', 'file_path')
>>>>>>> e2147defc2401c88eeef7eac9411b5da21982db5
    list_display_links = ('title', 'description')
    search_fields = ('title', 'description')
    list_filter = ()
    preserve_filters = False
    date_hierarchy = 'published'
    readonly_fields = ('published',)
    actions = ('discount',)

    def discount(self, request, queryset):
        f = F('title')
        for rec in queryset:
            rec.price = f / 2
            rec.save()
        self.message_user(request, 'mission complete')

    discount.short_description = 'Уменьшить цену вдвое'

    def get_fieldsets(self, request, obj=None):
        fieldsets = (
            (None, {
                'fields': ('title', 'description', 'rubric'),
                'classes': ('wide',),
            }),
            ('Дополнительные сведения', {
                'fields': ('file_path',),
                'description': 'Параметры, необязательные для указания.',
            }),
            ('Автоматически присваиваемое поля', {
                'fields': ('published',),

            })
        )
        return fieldsets
    autocomplete_fields = ('rubric',)
    # raw_id_fields = ('rubric',)
    # def view_on_site(self, rec):
    #     return reverse('news_output:detail', kwargs={'pk': rec.pk})







admin.site.register(News, NewsAdmin)
admin.site.register(Rubric,  RubricAdmin)

