from rest_framework.authtoken import views
from rest_framework.authtoken.models import Token
from rest_framework.response import Response


class ObtainAuthToken(views.ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        groups = [g.name for g in user.groups.all()]
        return Response({
                'token': token.key,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_superuser': user.is_superuser,
                'groups': groups
        })


obtain_auth_token = ObtainAuthToken.as_view()

