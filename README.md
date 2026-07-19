 Architektura i komponenty systemu

System składa się z czterech warstw logicznych, które integrują się w celu zapewnienia ciągłej integracji, bezpiecznego wdrażania oraz monitorowania w czasie rzeczywistym.

1. Warstwa Aplikacyjna (FastAPI)

Aplikacja została zbudowana przy użyciu frameworka FastAPI.
 
Endpointy: Implementuje `/health` (używany przez Kubernetes do sond `liveness` i `readiness`) oraz `/metrics` (udostępnia metryki w formacie kompatybilnym z Prometheus).
Zasady działania: Aplikacja działa na porcie 8080. Jest to lekki serwis typu event-driven, który po każdym zapytaniu aktualizuje wewnętrzny licznik operacji, co pozwala na wizualizację ruchu w Grafanie.

2. Konteneryzacja (Docker)

Obraz kontenera został zoptymalizowany pod kątem bezpieczeństwa i wydajności:

Multi-stage build: Proces budowania podzielony jest na etapy (budowanie zależności i artefaktów w osobnym środowisku), co pozwala na uzyskanie finalnego obrazu zawierającego tylko niezbędne pliki wykonawcze, minimalizując powierzchnię ataku.
Bezpieczeństwo (Non-root): Aplikacja uruchamiana jest z uprawnieniami użytkownika `appuser` (nie `root`), co jest standardem bezpieczeństwa w środowiskach produkcyjnych.

 3. Orkiestracja (Kubernetes & Helm)

Zarządzanie infrastrukturą odbywa się za pomocą narzędzi Kubernetes (Kind) oraz Helm:

Helm: Pełni rolę menedżera pakietów. Dzięki szablonowaniu (templates), umożliwia parametryzację konfiguracji (np. liczba replik, porty, zmienne środowiskowe) w pliku `values.yaml`.
ServiceMonitor: Jest to zasob typu Custom Resource Definition (CRD), który automatycznie rejestruje usługę wewnątrz klastra Prometheusa, eliminując potrzebę ręcznej konfiguracji endpointów skrapowania metryk.

4. CI/CD (GitHub Actions)

Pipeline został został podzielony oddzielnie na CI i CD

CI : Odpala się przy każdym wypchnięciu kodu. Obejmuje budowanie obrazu oraz skanowanie narzędziem Trivy w poszukiwaniu podatności krytycznych i wysokich. Blokuje budowanie w przypadku naruszeń bezpieczeństwa.
CD : Uruchamiany wyłącznie przy scalaniu z gałęzią główną. Odpowiada za budowę obrazu produkcyjnego, tagowanie go unikalnym hashem commita (`git SHA`) i publikację w rejestrze GHCR.

5. Obserwowalność (Prometheus & Grafana)

Stack monitorujący oparty jest na `kube-prometheus-stack`. Prometheus pełni rolę serwera zbierającego szeregi czasowe (metrics scraping), natomiast Grafana służy jako warstwa prezentacji danych, umożliwiając wizualizację wydajności i obciążenia mikroserwisu.



 Instrukcja wdrożenia

1. Przygotowanie środowiska (Klaster i Monitoring)

Wymagane jest zainstalowanie narzędzi `kind`, `helm` oraz `kubectl`.


 Inicjalizacja klastra Kind
kind create cluster --name dev-ops-cluster

 Instalacja stacku monitoringu
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install monitoring prometheus-community/kube-prometheus-stack


 Budowa lokalna
docker build -t devops-app:local ./app
kind load docker-image devops-app:local --name dev-ops-cluster

 Instalacja za pomocą Helm
helm install my-app ./helm



 3. Weryfikacja

Po wdrożeniu można sprawdzić status podów oraz przekierować porty w celu uzyskania dostępu do usług:

Dostęp do aplikacji:
kubectl port-forward svc/my-app-service 8080:8080
# URL: http://localhost:8080




Dostęp do Grafany

# Pobranie hasła:
kubectl get secret monitoring-grafana -o jsonpath="{.data.admin-password}" | base64 --decode

# Przekierowanie:
kubectl port-forward svc/monitoring-grafana 3000:80
# URL: http://localhost:3000
 