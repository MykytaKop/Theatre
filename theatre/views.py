from datetime import datetime

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.response import Response
from rest_framework import viewsets, status
from django.db.models import F, Count
from rest_framework.pagination import PageNumberPagination

from .permissions import IsAdminOrIfAuthenticatedReadOnly
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .models import Play, Genre, Actor, TheatreHall, Performance, Reservation
from .serializers import (
    PlaySerializer,
    PlayListSerializer,
    PlayDetailSerializer,
    PlayImageSerializer,
    GenreSerializer,
    ActorSerializer,
    TheatreHallSerializer,
    PerformanceSerializer,
    PerformanceListSerializer,
    PerformanceDetailSerializer,
    ReservationSerializer,
    ReservationListSerializer,
)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class PlayViewSet(viewsets.ModelViewSet):
    queryset = Play.objects.prefetch_related("genres", "actors")
    serializer_class = PlaySerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    @staticmethod
    def _params_to_ints(qs):
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        """Retrieve the movies with filters"""
        title = self.request.query_params.get("title")
        genres = self.request.query_params.get("genres")
        actors = self.request.query_params.get("actors")

        queryset = self.queryset

        if title:
            queryset = queryset.filter(title__icontains=title)

        if genres:
            genres_ids = self._params_to_ints(genres)
            queryset = queryset.filter(genres__id__in=genres_ids)

        if actors:
            actors_ids = self._params_to_ints(actors)
            queryset = queryset.filter(actors__id__in=actors_ids)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return PlayListSerializer

        if self.action == "retrieve":
            return PlayDetailSerializer

        if self.action == "upload_image":
            return PlayImageSerializer

        return PlaySerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to specific movie"""
        movie = self.get_object()
        serializer = self.get_serializer(movie, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "genres",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by genre id (ex. ?genres=2,5)",
            ),
            OpenApiParameter(
                "actors",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by actor id (ex. ?actors=2,5)",
            ),
            OpenApiParameter(
                "title",
                type=OpenApiTypes.STR,
                description="Filter by play title (ex. ?title=fiction)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class TheatreHallViewSet(viewsets.ModelViewSet):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = (
        Performance.objects.all()
        .select_related("play", "theatre_hall")
        .annotate(
            tickets_available=(
                F("theatre_hall__rows") * F("theatre_hall__seats_in_row")
                - Count("tickets")
            )
        )
    )
    serializer_class = PerformanceSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        date = self.request.query_params.get("date")
        play_id_str = self.request.query_params.get("play")

        queryset = self.queryset

        if date:
            date = datetime.strptime(date, "%Y-%m-%d").date()
            queryset = queryset.filter(show_time__date=date)

        if play_id_str:
            queryset = queryset.filter(play_id=int(play_id_str))

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PerformanceListSerializer

        if self.action == "retrieve":
            return PerformanceDetailSerializer

        return PerformanceSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "movie",
                type=OpenApiTypes.INT,
                description="Filter by movie id (ex. ?movie=2)",
            ),
            OpenApiParameter(
                "date",
                type=OpenApiTypes.DATE,
                description=(
                    "Filter by datetime of MovieSession" " " "(ex. ?date=2022-10-23)"
                ),
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of plays"""
        return super().list(request, *args, **kwargs)


class ReservationPagination(PageNumberPagination):
    page_size = 5
    max_page_size = 100


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.prefetch_related(
        "tickets__performance__play", "tickets__performance__theatre_hall"
    )
    serializer_class = ReservationSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = ReservationPagination

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return ReservationListSerializer

        return ReservationSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
