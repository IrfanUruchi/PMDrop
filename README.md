# PMDrop

PMDrop is a self-hosted LAN file transfer application designed for fast and private sharing between devices connected to the same local network.

The project combines a FastAPI backend with a browser-based frontend and uses WebRTC to establish direct peer-to-peer connections whenever possible. The backend is responsible for device discovery, signaling, and metadata management, while the actual file transfer takes place directly between connected devices. This keeps the server lightweight and allows transfers to fully utilize the available local network bandwidth.

The idea behind PMDrop was to build a simple file sharing solution that can run anywhere without depending on external cloud services or platform-specific ecosystems. Everything is accessible through the browser, making it possible to share files between Windows, Linux, macOS, Raspberry Pi devices, and any other system capable of running a modern web browser.

The application currently supports transferring both individual files and entire folders using drag and drop, maintains a local transfer history through SQLite, and can be deployed with a single Docker command. The same Docker image supports both AMD64 and ARM64 platforms, allowing the project to run unchanged on desktop computers, servers, and Raspberry Pi devices.

---

## Architecture

PMDrop follows a lightweight client-server architecture where the server coordinates communication while clients exchange data directly whenever possible.

```
                 Browser
                     │
          FastAPI Backend
                     │
      Device Discovery & Signaling
                     │
          WebRTC Negotiation
                     │
        Direct Peer Connection
                     │
          File / Folder Transfer
```

The FastAPI backend handles device registration, signaling, persistence, and transfer metadata. Once two devices complete the WebRTC negotiation process, the file transfer no longer passes through the server and continues directly between the participating devices.

---

## Quick Start

Pull the latest image from Docker Hub.

```bash
docker pull irfanuruchi/pmdrop:latest
```

Run PMDrop.

```bash
docker run -d \
  --name pmdrop \
  --restart unless-stopped \
  -p 8000:8000 \
  -v pmdrop_data:/app/backend/data \
  -v pmdrop_storage:/app/backend/storage \
  irfanuruchi/pmdrop:latest
```

Once the container starts, open your browser and navigate to

```
http://localhost:8000
```

or from another device on the same network

```
http://<server-ip>:8000
```

---

## Persistent Data

PMDrop stores all persistent data inside Docker volumes.

| Volume | Purpose |
|---------|---------|
| `pmdrop_data` | SQLite database |
| `pmdrop_storage` | Uploaded files and transferred folders |

Updating the container does not remove existing data.

---

## Docker Support

PMDrop is distributed as a multi-architecture Docker image supporting both AMD64 and ARM64 platforms.

```
linux/amd64
linux/arm64
```

Docker automatically downloads the correct image for the host system, allowing the same deployment command to be used on desktop computers, servers, and Raspberry Pi devices.

---

## Project Structure

```
PMDrop/
├── backend/
│   ├── app/
│   ├── storage/
│   └── requirements.txt
├── frontend/
├── Dockerfile
├── docker-compose.yml
└── README.md
```

The backend contains the FastAPI application together with the database models, REST API, signaling logic, and file management. The frontend provides the browser interface used for device discovery and transfers, while Docker files allow the entire application to be deployed as a single container.

---

## Roadmap

PMDrop is still under active development. Future work includes improving device discovery, adding a native desktop client, introducing QR code pairing for mobile devices, expanding transfer management with pause and resume support, and improving transfer statistics and monitoring.

---

## License

This project is released under the MIT License.
