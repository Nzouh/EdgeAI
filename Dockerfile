# STAGE 1: Build the C++ Engine
FROM alpine:latest AS builder
RUN apk add --no-cache build-base

WORKDIR /build
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
