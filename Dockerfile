FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt ./
RUN pip install --prefix=/install -r requirements.txt

FROM python:3.12-slim
ENV PORT=8050
WORKDIR /app
COPY --from=builder /install /usr/local
COPY . .
EXPOSE $PORT
CMD ["python", "-m", "src.main"]
