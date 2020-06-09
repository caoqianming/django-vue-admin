
from rest_framework import serializers



# class TreeSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     label = serializers.CharField(max_length=20, source='name')
#     pid = serializers.PrimaryKeyRelatedField(read_only=True)


# class TreeAPIView(ListAPIView):
#     """
#     自定义树结构View
#     """
#     serializer_class = TreeSerializer

#     def list(self, request, *args, **kwargs):
#         queryset = self.filter_queryset(self.get_queryset())
#         page = self.paginate_queryset(queryset)
#         serializer = self.get_serializer(queryset, many=True)
#         tree_dict = {}
#         tree_data = []
#         try:
#             for item in serializer.data:
#                 tree_dict[item['id']] = item
#             for i in tree_dict:
#                 if tree_dict[i]['pid']:
#                     pid = tree_dict[i]['pid']
#                     parent = tree_dict[pid]
#                     parent.setdefault('children', []).append(tree_dict[i])
#                 else:
#                     tree_data.append(tree_dict[i])
#             results = tree_data
#         except KeyError:
#             results = serializer.data
#         if page is not None:
#             return self.get_paginated_response(results)
#         return Response(results)
