import cv2
import boto3
import time
import threading
import os

# Inicialize a webcam
cap = cv2.VideoCapture(0)

# Inicialize o cliente AWS Rekognition
rekognition_client = boto3.client('rekognition')

# Definir o caminho para a pasta onde os rostos armazenados estão
pasta_rostos_armazenados = "rostos_armazenados/"  # Mude para o caminho correto da sua pasta de imagens

def comparar_com_rostos_armazenados(frame_capturado):
    # Converte o frame capturado (da webcam) para bytes
    _, buffer = cv2.imencode('.jpg', frame_capturado)
    frame_bytes = buffer.tobytes()

    # Percorre todas as imagens na pasta de rostos armazenados
    for arquivo_imagem in os.listdir(pasta_rostos_armazenados):
        caminho_imagem = os.path.join(pasta_rostos_armazenados, arquivo_imagem)

        # Leia a imagem armazenada
        with open(caminho_imagem, 'rb') as imagem_armazenada:
            armazenada_bytes = imagem_armazenada.read()

        try:
            # Usa a API Rekognition para comparar os rostos
            resposta_comparacao = rekognition_client.compare_faces(
                SourceImage={'Bytes': frame_bytes},  # Imagem capturada da webcam
                TargetImage={'Bytes': armazenada_bytes},  # Imagem armazenada
                SimilarityThreshold=95,  # Define a similaridade mínima de 95%
                QualityFilter='AUTO'  # Ajusta a filtragem de qualidade automaticamente
            )

            # Se encontrar uma correspondência, exiba o nome do arquivo correspondente
            if resposta_comparacao['FaceMatches']:
                for faceMatch in resposta_comparacao['FaceMatches']:
                    similaridade = faceMatch['Similarity']
                    print(f"Rosto correspondente encontrado: {arquivo_imagem} com {similaridade:.2f}% de similaridade")
            else:
                print(f"x")

        except Exception as e:
            print(f"x")

# Controle de taxa de análise (0.5 imagens por segundo)
intervalo_entre_frames = 2  # 0.5 imagens por segundo
ultimo_tempo_analise = time.time()  # Inicializa o tempo de última análise

# Função para rodar a comparação em segundo plano
def analisar_rostos(frame):
    comparar_com_rostos_armazenados(frame)

while True:
    ret, frame = cap.read()  # Captura o frame da webcam
    if ret:
        # Exibe o vídeo em tempo real
        cv2.imshow('Webcam', frame)

        # Verifica se já se passou o tempo suficiente para análise
        tempo_atual = time.time()
        if (tempo_atual - ultimo_tempo_analise) >= intervalo_entre_frames:
            # Inicia um thread para rodar a detecção em paralelo
            threading.Thread(target=analisar_rostos, args=(frame,)).start()
            ultimo_tempo_analise = tempo_atual  # Atualiza o tempo da última análise

        # Exibe o resultado da última detecção (em paralelo)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
