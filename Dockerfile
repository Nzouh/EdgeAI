# STAGE 1: Build the C++ Engine
FROM alpine:latest AS builder
RUN apk add --no-cache build-base curl

WORKDIR /build

# Download header-only web server library directly in Linux environment
RUN curl -L -o httplib.h https://raw.githubusercontent.com/yhirose/cpp-httplib/v0.15.3/httplib.h

# Copy only the code we need to compile
COPY compiler/ /build/

# Compile statically so it runs on ANY linux (Even if they don't have our libraries)
RUN g++ -static -O3 -o sentinel_engine main.cpp
RUN g++ -static -O3 -o validator_tool validator.cpp

# STAGE 2: Deployment (The "Product")
FROM alpine:latest
WORKDIR /app

# Copy only the brains and the binaries
COPY --from=builder /build/sentinel_engine .
COPY --from=builder /build/validator_tool .
COPY sentinel_model.bin .
COPY nasa_test_labeled.csv .

# Document that we use port 8080 (For future web dashboard)
EXPOSE 8080

# Run the engine by default
CMD ["./sentinel_engine"]
