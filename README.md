# gRPC-Microservices-Tutorial
Understanding and implementing a basic Microservice with Python's popular gRPC framework

*RPC* stands for **Google Remote Procedure Call** and *RPC* infrastructure is acutally called *gRPC* or **Google RPC**. It is built on top of HTTP/2.

Why should we use **Microservices**? There are a lot of reasons that you can find on Google, but to name a few benefits:

1. Microservices helps us to decouple our code and divide the modules in our application systematically, of course there should be seperate microservices for each module and no microservice should have unrelated functionality to the existing one.

2. One benefit of microservices is that teams can have clear ownership of their code. This makes it more likely that there will be a clear vision for the code and that the code will remain clean and organized.

3. If all your code is in one application, then you have to deploy it all at once. This is a big risk! It means a change to one small part of the code can take down the entire site.

4. Microservices gives us a lot of flexibility, you can write your microservices in a lot of different languages and make them all communicate with each other using simple client server cycle.


We will be using Python's popular *gRPC* for implementing our simple Microservice. *gRPC* has a lot of features, to name a few:

1. *gRPC* has built-in support for streaming requests and responses and it manages Network issues more gracefully than a basic HTTP connection, connecting automatically even after long disconnects.

2. Using ProtoBuf, *gRPC* allows you to define your protocol in a human readable way, with a lot of pre-defined types and you can even generate python code from a `.proto` file which provides basic validation and type checking automatically.

3. With *gRPC* you can define your API in terms of functions, not HTTP verbs and resources.


## Implementation

In this section, we'll define some microservices for your Online Books For You website. You’ll define an API for them and write the Python code that implements them as microservices as you go through this basic tutorial.

To keep things manageable, you’ll define only one microservice for Recommendations, which will provide a list of books in which the user may be interested.


Protocol Buffers have their own syntax through which we can define the flow of our Microservice, here is a simple proto file for our recommendations microservice:

**protobufs/recommendations.proto**
```
syntax = "proto3";

enum BookCategory {
    MYSTERY = 0;
    SCIENCE_FICTION = 1;
    GHOST_STORIES = 2;
}

message RecommendationRequest {
    int32 user_id = 1;
    BookCategory category = 2;
    int32 max_results = 3;
}

message BookRecommendation {
    int32 id = 1;
    string title = 2;
}

message RecommendationResponse {
    repeated BookRecommendation recommendations = 1;
}

service Recommendations {
    rpc Recommend (RecommendationRequest) returns (RecommendationRespoinse);
}
```

This Protocol Buffers file defines your API.

Above, the `repeated` keyword indicates that response actually has a list of Recommendations objects.

Now we generate the Python code from the proto file by running the following command,

```
# Run this inside a virtualenv
mkdir recommendations
cd recommendations
python -m grpc_tools.protoc -I ../protobufs/ --python_out=. --grpc_python_out=. ../protobufs/recommendations.proto
```

You will find multiple files generated in the recommendations folder since we passed the `--python_out=.` and told `grpc_tools.protoc` compiler to look for `.proto` files in the `../protobufs/` folder.

These files include Python types and functions to interact with your API. The compiler will generate client code to call an RPC and server code to implement the RPC. You’ll look at the client side first.

You can play around the auto generated code using python shell,

```
# CLIENT CODE
from recommendations_pb2 import BookCategory, RecommendationRequest

request = RecommendationRequest(user_id=1, category=BookCategory.GHOST_STORY, max_results=3)
request.category
request.max_results

# It even does type checking and validation for us and throws TypeError if the request is invalid
request = RecommendationRequest(user_id="some string", category=BookCategory.GHOST_STORY, max_results=3)


# SERVER CODE
import grpc
from recommendations_pb2_grpc import RecommendationsStub
channel = grpc.insecure_channel("localhost:50051")
client = RecommendationsStub(channel)
request = RecommendationRequest(user_id=1, category=BookCategory.GHOST_STORY, max_results=3)
client.Recommend(request)  # this line throws error since we are sending a request to server which is not running
```

`client.Recommend` comes from the second last line of the **protobuf/recommendations.proto** file `rpc Recommend (...) returns (...)`

### RPC Server
To run your RPC server, you need to write a Service class inheriting `recommendations_pb2_grpc.RecommendationsServicer` and then add this service to the recommendations servicer,

For complete code, checkout **recommendations/recommendations.py**
```
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    recommendations_pb2_grpc.add_RecommendationsServicer_to_server(
        RecommendationService(), server
    )
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
```

Now we can run the server using, `python recommendations.py` and then simply run the `client.Recommend(request)` again and you should get the response from your microservice.



**NOTE:** For complete article with proper details and usage along with code snippets, checkout [realpython-microservices-grp](https://realpython.com/python-microservices-grpc/)

To deploy your Python Microservice in a Production ready environment, checkout [production-ready-python-microservices](https://realpython.com/python-microservices-grpc/#production-ready-python-microservices)
