from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .serializers import (
    LoginSerializer,
    IzohSerializer,
    MessageResponseSerializer,
    PostSerializer,
    PostBatafsilSerializer,
    ProfilSerializer,
    RegisterSerializer,
    TokenResponseSerializer,
)
from rest_framework import viewsets
from rest_framework.decorators import action
from .permissions import FaqatMuallifOzgartiradi
from drf_spectacular.utils import extend_schema


from .forms import (
    FoydalanuvchiYangilashForma,
    PostForma,
    ProfilYangilashForma,
    RoyxatdanOtishForma,
)
from .models import Izoh, Like, Post, Profil


def post_batafsil(request, post_id):
    post = get_object_or_404(Post, id=post_id, nashr_etilgan=True)
    if request.method == 'POST':
        ism = request.POST.get('ism', '').strip()
        matn = request.POST.get('matn', '').strip()
        if ism and matn:
            Izoh.objects.create(post=post, ism=ism, matn=matn)
            return redirect('post_batafsil', post_id=post.id)
    Post.objects.filter(id=post.id).update(korildi=F('korildi') + 1)
    post.refresh_from_db()
    return render(request, 'blog/post_batafsil.html', {
        'post': post,
        'izohlar': post.izohlar.all(),
    })


@login_required
def post_yaratish(request):
    if request.method == 'POST':
        forma = PostForma(request.POST, request.FILES)
        if forma.is_valid():
            post = forma.save(commit=False)
            post.muallif = request.user
            post.save()
            messages.success(request, 'Post yaratildi!')
            return redirect('bosh_sahifa')
    else:
        forma = PostForma()
    return render(request, 'blog/post_yaratish.html', {'forma': forma})


@login_required
def post_tahrirlash(request, post_id):
    post = get_object_or_404(Post, id=post_id, muallif=request.user)
    if request.method == 'POST':
        forma = PostForma(request.POST, request.FILES, instance=post)
        if forma.is_valid():
            forma.save()
            messages.success(request, 'Post yangilandi!')
            return redirect('post_batafsil', post_id=post.id)
    else:
        forma = PostForma(instance=post)
    return render(request, 'blog/post_tahrirlash.html', {'forma': forma, 'post': post})


@login_required
def post_ochirish(request, post_id):
    post = get_object_or_404(Post, id=post_id, muallif=request.user)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post o‘chirildi!')
        return redirect('bosh_sahifa')
    return render(request, 'blog/post_ochirish.html', {'post': post})


def biz_haqimizda(request):
    return render(request, 'blog/biz_haqimizda.html')


def aloqa(request):
    return render(request, 'blog/aloqa.html')


def salomlash(request, ism):
    return render(request, 'blog/biz_haqimizda.html', {'ism': ism})


def ommabop_postlar(request):
    postlar = Post.objects.filter(nashr_etilgan=True).order_by('-korildi')
    return render(request, 'blog/ommabop.html', {'postlar': postlar})


def royxatdan_otish(request):
    if request.method == 'POST':
        forma = RoyxatdanOtishForma(request.POST)
        if forma.is_valid():
            user = forma.save()
            login(request, user)
            return redirect('bosh_sahifa')
    else:
        forma = RoyxatdanOtishForma()
    return render(request, 'blog/royxatdan_otish.html', {'forma': forma})


def kirish(request):
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password'),
        )
        if user is not None:
            login(request, user)
            return redirect('bosh_sahifa')
        messages.error(request, 'Login yoki parol noto‘g‘ri.')
    return render(request, 'blog/kirish.html')


def chiqish(request):
    logout(request)
    return redirect('bosh_sahifa')


def qidiruv(request):
    soz = request.GET.get('q', '').strip()
    postlar = Post.objects.filter(nashr_etilgan=True)
    if soz:
        postlar = postlar.filter(sarlavha__icontains=soz) | postlar.filter(matn__icontains=soz)
    return render(request, 'blog/qidiruv.html', {
        'postlar': postlar.distinct(),
        'qidiruv_sozi': soz,
    })


def profil(request, username):
    foydalanuvchi = get_object_or_404(User, username=username)
    postlar = Post.objects.filter(
        muallif=foydalanuvchi,
        nashr_etilgan=True,
    ).order_by('-yaratilgan_sana')
    return render(request, 'blog/profil.html', {
        'profil_egasi': foydalanuvchi,
        'postlar': postlar,
        'postlar_soni': postlar.count(),
    })

@login_required
def profil_tahrirlash(request, username):
    if username != request.user.username:
        return redirect('profil', username=request.user.username)

    if request.method == 'POST':
        f_forma = FoydalanuvchiYangilashForma(request.POST, instance=request.user)
        p_forma = ProfilYangilashForma(request.POST, request.FILES, instance=request.user.profil)

        if f_forma.is_valid() and p_forma.is_valid():
            f_forma.save()
            p_forma.save()
            messages.success(request, '✅ Profilingiz yangilandi!')
            return redirect('profil', username=request.user.username)
    else:
        f_forma = FoydalanuvchiYangilashForma(instance=request.user)
        p_forma = ProfilYangilashForma(instance=request.user.profil)

    context = {
        'f_forma': f_forma,
        'p_forma': p_forma
    }
    return render(request, 'blog/profil_tahrirlash.html', context)

def bosh_sahifa(request):
    postlar_list = Post.objects.select_related('muallif').filter(
        nashr_etilgan=True
    ).order_by('-yaratilgan_sana')

    # Har sahifada 5 ta post
    paginator = Paginator(postlar_list, 5)

    sahifa_raqami = request.GET.get('sahifa')
    postlar = paginator.get_page(sahifa_raqami)

    return render(request, 'blog/bosh.html', {'postlar': postlar})


@extend_schema(exclude=True)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def post_list_api(request):
    """Postlarni olish yoki yangi post yaratish."""
    if request.method == 'GET':
        postlar = Post.objects.filter(nashr_etilgan=True).order_by('-yaratilgan_sana')
        serializer = PostSerializer(postlar, many=True)
        return Response(serializer.data)

    serializer = PostSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(muallif=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(exclude=True)
@api_view(['GET'])
def post_detail_api(request, post_id):
    """Bitta e'lonni olish va ko'rishlar sonini oshirish."""
    try:
        post = Post.objects.get(id=post_id, nashr_etilgan=True)
    except Post.DoesNotExist:
        return Response(
            {'xato': 'Post topilmadi'},
            status=status.HTTP_404_NOT_FOUND,
        )

    post.korildi += 1
    post.save(update_fields=['korildi'])
    serializer = PostSerializer(post)
    return Response(serializer.data)


@extend_schema(exclude=True)
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def post_update_api(request, post_id):
    """Postni faqat uning muallifi yangilashi mumkin."""
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response(
            {'xato': 'Post topilmadi'},
            status=status.HTTP_404_NOT_FOUND,
        )

    if post.muallif != request.user:
        return Response(
            {'xato': "Ruxsat yo'q"},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = PostSerializer(post, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(exclude=True)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def post_delete_api(request, post_id):
    """Postni faqat uning muallifi o'chirishi mumkin."""
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response(
            {'xato': 'Post topilmadi'},
            status=status.HTTP_404_NOT_FOUND,
        )

    if post.muallif != request.user:
        return Response(
            {'xato': "Ruxsat yo'q"},
            status=status.HTTP_403_FORBIDDEN,
        )

    post.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    request=LoginSerializer,
    responses=TokenResponseSerializer,
)
@api_view(['POST'])
def login_api(request):
    """API orqali foydalanuvchini tizimga kiritadi."""
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)

    if user is None:
        return Response(
            {'xato': "Noto'g'ri login yoki parol"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    token, _ = Token.objects.get_or_create(user=user)
    return Response({
        'token': token.key,
        'user_id': user.id,
        'username': user.username,
    })


@extend_schema(request=None, responses=MessageResponseSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_api(request):
    """Joriy foydalanuvchining tokenini bekor qiladi."""
    Token.objects.filter(user=request.user).delete()
    return Response({'xabar': 'Muvaffaqiyatli chiqildi'})


@extend_schema(
    request=RegisterSerializer,
    responses=TokenResponseSerializer,
)
@api_view(['POST'])
def register_api(request):
    """Yangi foydalanuvchi yaratadi va token qaytaradi."""
    username = request.data.get('username', '').strip()
    email = request.data.get('email', '').strip()
    password = request.data.get('password', '')

    if not username or not password:
        return Response(
            {'xato': 'username va password majburiy'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {'xato': 'Bu username band'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
    )
    token = Token.objects.create(user=user)
    return Response({
        'token': token.key,
        'user_id': user.id,
        'username': user.username,
    }, status=status.HTTP_201_CREATED)


class PostViewSet(viewsets.ModelViewSet):
    """
    Post lar uchun ViewSet
    - list: Barcha postlar
    - create: Yangi post
    - retrieve: Bitta post
    - update: Postni yangilash
    - destroy: Postni o'chirish
    """
    queryset = Post.objects.filter(nashr_etilgan=True).order_by('-yaratilgan_sana')
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, FaqatMuallifOzgartiradi]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['muallif', 'nashr_etilgan']
    search_fields = ['sarlavha', 'matn']
    ordering_fields = ['yaratilgan_sana', 'korildi']

    def get_serializer_class(self):
        if self.action == 'retrieve' and self.request.version == 'v2':
            return PostBatafsilSerializer
        return PostSerializer

    def perform_create(self, serializer):
        """Yangi post yaratishda muallif ni avtomatik qo'shish"""
        serializer.save(muallif=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        post = self.get_object()
        like, created = Like.objects.get_or_create(user=request.user, post=post)

        if not created:
            like.delete()
            return Response({'xabar': 'Like olib tashlandi'})

        return Response({'xabar': 'Like qo‘yildi'}, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        """Bitta post olishda korildi sonini oshirish"""
        instance = self.get_object()
        instance.korildi += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def ommabop(self, request):
        """Eng ko'p ko'rilgan postlar"""
        postlar = Post.objects.filter(nashr_etilgan=True).order_by('-korildi')[:5]
        serializer = self.get_serializer(postlar, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def mening_postlarim(self, request):
        """Foydalanuvchining o'z postlari"""
        if not request.user.is_authenticated:
            return Response(
                {'xato': 'Tizimga kirish kerak'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        postlar = Post.objects.filter(muallif=request.user).order_by('-yaratilgan_sana')
        serializer = self.get_serializer(postlar, many=True)
        return Response(serializer.data)


class IzohViewSet(viewsets.ModelViewSet):
    queryset = Izoh.objects.all().order_by('-yaratilgan_sana')
    serializer_class = IzohSerializer


class ProfilViewSet(viewsets.ModelViewSet):
    queryset = Profil.objects.select_related('foydalanuvchi').all()
    serializer_class = ProfilSerializer
