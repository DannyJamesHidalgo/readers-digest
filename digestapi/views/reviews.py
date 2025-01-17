from rest_framework import viewsets, status, serializers, permissions
from rest_framework.response import Response
from digestapi.models import BookReviews, Book


class ReviewSerializer(serializers.ModelSerializer):
    is_owner = serializers.SerializerMethodField()

    def get_is_owner(self, obj):
        # Check if the user is the owner of the review
        return self.context["request"].user == obj.user

    class Meta:
        model = BookReviews
        fields = ["id", "book", "user", "rating", "comment", "created_at", "is_owner"]
        read_only_fields = ["user"]


class ReviewViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def list(self, request):
        # Get all reviews
        reviews = BookReviews.objects.all()

        # Serialize the objects, and pass request to determine owner
        serializer = ReviewSerializer(reviews, many=True, context={"request": request})

        # Return the serialized data with 200 status code
        return Response(serializer.data)

    def create(self, request):
        # Create a new instance of a review and assign property
        # values from the request payload using `request.data`
        book = request.data.get("book")
        rating = request.data.get("rating")
        comment = request.data.get("comment")
        new_review = BookReviews()
        new_review.book = Book.objects.get(id=book)
        new_review.rating = rating
        new_review.comment = comment
        new_review.user = request.user
        new_review.save()

        # Save the review

        try:
            # Serialize the objects, and pass request as context
            serialized_review = ReviewSerializer(
                new_review, many=False, context={"request": request}
            )
            # Return the serialized data with 201 status code
            return Response(serialized_review.data, status=status.HTTP_201_CREATED)

        except Exception as ex:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        try:
            # Get the requested review
            review = BookReviews.objects.get(pk=pk)
            serialized = ReviewSerializer(
                review, many=False, context={"request": request}
            )
            return Response(serialized.data, status=status.HTTP_200_OK)

            # Serialize the object (make sure to pass the request as context)

            # Return the review with 200 status code

        except BookReviews.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            # Get the requested review
            review = BookReviews.objects.get(pk=pk)

            # Check if the user has permission to delete
            # Will return 403 if authenticated user is not author
            if review.user.id != request.user.id:
                return Response(status=status.HTTP_403_FORBIDDEN)

            # Delete the review
            review.delete()

            # Return success but no body
            return Response(status=status.HTTP_204_NO_CONTENT)

        except BookReviews.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
