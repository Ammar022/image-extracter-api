source ./scripts/env.sh

echo "Building $PROJECT_NAME..."
./scripts/build.sh || exit 1

echo "Executing $PROJECT_NAME..."
./$PROJECT_NAME -link $1 -dir $2