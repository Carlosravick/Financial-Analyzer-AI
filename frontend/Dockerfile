FROM node:20-alpine

WORKDIR /app

# Copia apenas os arquivos de dependência primeiro (otimiza o cache do Docker)
COPY package*.json ./

# Instala as dependências
RUN npm install

# Copia o resto do código
COPY . .

# Expõe a porta do Next.js
EXPOSE 3000

# Roda o servidor de desenvolvimento
CMD ["npm", "run", "dev"]