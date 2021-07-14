from concurrent import futures

import random
import grpc

from recommendations_pb2 import BookCategory, BookRecommendation, RecommendationResponse
import recommendations_pb2_grpc


books_by_category = {
    BookCategory.MYSTERY: [
        BookRecommendation(id=1, title="The Maltese Falcon"),
        BookRecommendation(id=2, title="Murder on the Orient Express"),
        BookRecommendation(id=3, title="The Hound of the Baskervilles"),
    ],
    BookCategory.SCIENCE_FICTION: [
        BookRecommendation(id=4, title="The Hitchhiker's Guide to the Galaxy"),
        BookRecommendation(id=5, title="Ender's Game"),
        BookRecommendation(id=6, title="The Dune Chronicles"),
    ],
    BookCategory.GHOST_STORIES: [
        BookRecommendation(id=7, title="Hardy Boys"),
        BookRecommendation(id=8, title="Tintin & Ghost Adventures"),
        BookRecommendation(id=9, title="Ghost Adventurures"),
    ],
}


class RecommendationService(recommendations_pb2_grpc.RecommendationsServicer):
    def Recommend(self, request, context):
        if request.category not in books_by_category:
            context.abort(grpc.StatusCode.NOT_FOUND, "No books for {} category".format(request.category))

        books_for_category = books_by_category[request.category]
        num_results = min(request.max_results, len(books_for_category))

        books_to_recommend = random.sample(books_for_category, num_results)

        return RecommendationResponse(recommendations=books_to_recommend)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    recommendations_pb2_grpc.add_RecommendationsServicer_to_server(RecommendationService(), server)

    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
