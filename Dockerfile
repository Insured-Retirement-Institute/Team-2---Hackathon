FROM ghcr.io/cloudnative-pg/postgresql:18-standard-trixie AS build

#  CNPG now comes with:
#   PGAudit
#   postgres failover slots
#   llvm jit support
#   pgvector
#   pgcrypto (contrib module, included in -standard- image, enable with CREATE EXTENSION pgcrypto)

USER root

RUN set -xe; \
	apt-get update; \
	apt-get install -y --no-install-recommends \
		python3-pip \
		build-essential \
		postgresql-server-dev-18 \
		libcurl4-openssl-dev \
		git \
		cmake \
		ninja-build \
		pkg-config \
		libssl-dev \
		liblz4-dev \
		libc++-dev \
		libc++abi-dev \
		libicu-dev ; \
	pip3 install --break-system-packages pgxnclient; \
	rm -rf /var/lib/apt/lists/*

RUN pgxn install pgmq

# TODO: may want to update this to pull a certain tag/release
RUN set -xe; \
	git clone --depth 1 https://github.com/duckdb/pg_duckdb.git /tmp/pg_duckdb; \
	cd /tmp/pg_duckdb; \
	git submodule update --init --recursive; \
	make -j$(nproc); \
	make install; \
	rm -rf /tmp/pg_duckdb


FROM ghcr.io/cloudnative-pg/postgresql:18-standard-trixie

# Copy built extensions from the build stage
COPY --from=build /usr/lib/postgresql/18/lib/ /usr/lib/postgresql/18/lib/
COPY --from=build /usr/share/postgresql/18/extension/ /usr/share/postgresql/18/extension/

# TODO: TimescaleDB
# Timescale does not exist in pgxn. Manual install required.
# Instructions from: https://www.tigerdata.com/docs/self-hosted/latest/install/installation-linux
# sudo apt install gnupg postgresql-common apt-transport-https lsb-release wget
# sudo /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh
# echo "deb https://packagecloud.io/timescale/timescaledb/debian/ $(lsb_release -c -s) main" | sudo tee /etc/apt/sources.list.d/timescaledb.list
# wget --quiet -O - https://packagecloud.io/timescale/timescaledb/gpgkey | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/timescaledb.gpg
# sudo apt update
# sudo apt install timescaledb-2-postgresql-18 postgresql-client-18
# sudo timescaledb-tune May want to run in some other startup script?

# TODO: TimescaleDB
# Timescale does not exist in pgxn. Manual install required.
# Instructions from: https://www.tigerdata.com/docs/self-hosted/latest/install/installation-linux

# https://github.com/supabase/wrappers would also be cool, lots of FDWs, maybe more stable than pg_duckdb
# / more future proof.
# TODO: pg_graphql would be cool
# pg_graphql is a PostgreSQL extension that enables querying the database with GraphQL using a single SQL function.
# Install https://supabase.github.io/pg_graphql/installation/

USER root
RUN set -xe; \
	apt-get update; \
	apt-get install -y --no-install-recommends \
		libcurl4 \
		libicu76 \
		liblz4-1 ; \
	rm -rf /var/lib/apt/lists/*

# Change to the uid of postgres (26)
USER 26
