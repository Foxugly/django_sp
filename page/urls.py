from tools.generic_urls import add_url_from_generic_views


app_name = 'page'
urlpatterns = [

              ] + add_url_from_generic_views('page.views')

#     path('pair/', PairListView.as_view(), name='pair_list'),
#     path('pair/add/', PairCreateView.as_view(), name="pair_add"),
#     path('pair/<int:pk>/change/', PairUpdateView.as_view(), name="pair_change"),
#     path('pair/<int:pk>/', PairDetailView.as_view(), name="pair_detail"),
#     path('pair/<int:pk>/delete', PairDeleteView.as_view(), name="pair_delete"),
#
#     path('document/', DocumentListView.as_view(), name='document_list'),
#     path('document/add/', DocumentCreateView.as_view(), name="document_add"),
#     path('document/<int:pk>/change/', DocumentUpdateView.as_view(), name="document_change"),
#     path('document/<int:pk>/', DocumentDetailView.as_view(), name="document_detail"),
#     path('document/<int:pk>/delete', DocumentDeleteView.as_view(), name="document_delete"),
#
#     path('item/', ItemListView.as_view(), name='item_list'),
#     path('item/add/', ItemCreateView.as_view(), name="item_add"),
#     path('item/<int:pk>/change/', ItemUpdateView.as_view(), name="item_change"),
#     path('item/<int:pk>/', ItemDetailView.as_view(), name="item_detail"),
#     path('item/<int:pk>/delete', ItemDeleteView.as_view(), name="item_delete"),
#
#     path('collection/', CollectionListView.as_view(), name='collection_list'),
#     path('collection/add/', CollectionCreateView.as_view(), name="collection_add"),
#     path('collection/<int:pk>/change/', CollectionUpdateView.as_view(), name="collection_change"),
#     path('collection/<int:pk>/', CollectionDetailView.as_view(), name="collection_detail"),
#     path('collection/<int:pk>/delete', CollectionDeleteView.as_view(), name="collection_delete"),
#
#     path('page/', PageListView.as_view(), name='page_list'),
#     path('page/add/', PageCreateView.as_view(), name="page_add"),
#     path('page/<int:pk>/change/', PageUpdateView.as_view(), name="page_change"),
#     path('page/<int:pk>/', PageDetailView.as_view(), name="page_detail"),
#     path('page/<int:pk>/delete', PageDeleteView.as_view(), name="page_delete"),
# ]
