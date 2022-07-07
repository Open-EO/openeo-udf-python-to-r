ARG SPARK_VERSION
ARG PYTHON_PACKAGE

FROM almalinux:8.5 as build

ARG SPARK_VERSION
ARG PYTHON_PACKAGE

COPY vito.repo /etc/yum.repos.d/vito.repo

WORKDIR /opt/spark/work-dir

RUN adduser -u 18585 -d /opt/spark/work-dir spark && \
    chown 18585:18585 /opt/spark/work-dir

RUN yum install -y epel-release
RUN yum install -y dnf --enablerepo=powertools spark-bin-${SPARK_VERSION}
RUN yum install -y --enablerepo=powertools \
    gdal-3.4.0 \
    gdal-devel-3.4.0 \
    python38-gdal-3.4.0 \
    gdal-libs-3.4.0 \
    unzip \
    java-11-openjdk-headless \
    krb5-workstation \
    krb5-libs \
    sssd-client \
    ipa-client \
    nss \
    orfeo-toolbox-py38 \
    procps-ng \
    ${PYTHON_PACKAGE} \
    python38-pytz  \
    python38-Cython \
    fftw-libs-double \
    fftw-libs-single \
    openeo-vito-aux-data \
    tinyxml \
    compat-libgfortran-48-4.8.5-36.1.el8.x86_64 && \
    ln -s /usr/lib64/libgdal.so.30 /usr/lib64/libgdal.so.26 && \
    ln -s /usr/lib64/libgdal.so.30 /usr/lib64/libgdal.so.27 && \
    pip3 install --upgrade pip setuptools && \
    rm -r /root/.cache && \
    yum clean all && \
    rm -rf /var/cache/yum/*

ENV SPARK_HOME /usr/local/spark
ENV JAVA_HOME /usr/lib/jvm/jre
ENV PYSPARK_PYTHON=python3
ENV HADOOP_HOME=/usr/hdp/current/hadoop-client
ENV HADOOP_CONF_DIR=/etc/hadoop/conf
ENV YARN_CONF_DIR=/etc/hadoop/conf
ENV ACCUMULO_CLIENT_CONF_PATH=client.conf
ENV OTB_HOME=/usr
ENV OTB_APPLICATION_PATH=/usr/lib/otb/applications

# EP: install R, system requirements of R-spatial packages, and R package stars
# from: https://github.com/r-hub/r-minimal

ENV _R_SHLIB_STRIP_=true

ARG R_VERSION=4.2.1

WORKDIR /root

RUN yum install -y wget
RUN if [[ "$R_VERSION" == "devel" ]]; then                                   \
        wget https://cran.r-project.org/src/base-prerelease/R-devel.tar.gz;  \
    elif [[ "$R_VERSION" == "next" ]]; then                                  \
        wget https://cran.rstudio.com/src/base-prerelease/R-latest.tar.gz -O R-next.tar.gz; \
    else                                                                     \
        wget https://cran.rstudio.com/src/base/R-${R_VERSION%%.*}/R-${R_VERSION}.tar.gz; \
    fi
RUN tar xzf R-${R_VERSION}.tar.gz

# The directory inside the tarball sometimes has different names

RUN if [[ -e R-patched ]]; then	mv R-patched R-next; fi
RUN if [[ -e R-beta ]]; then mv R-beta R-next; fi
RUN if [[ -e R-alpha ]]; then mv R-alpha R-next; fi
RUN if [[ -e R-rc ]]; then mv R-rc R-next; fi
RUN if [[ -e R-prerelease ]]; then mv R-prerelease R-next; fi
RUN if [[ -e R-pre ]]; then mv R-pre R-next; fi

RUN yum install -y gcc gcc-c++ gcc-gfortran zlib-devel bzip2-devel xz-devel pcre2-devel libcurl-devel make perl

RUN cd R-${R_VERSION} &&                                                 \
    CXXFLAGS=-D__MUSL__  ./configure                                     \
        --with-recommended-packages=no                                   \
        --with-readline=no --with-x=no --enable-java=no                 \
        --enable-R-shlib                                                 \
        --disable-openmp --with-internal-tzcode
RUN cd R-${R_VERSION} && make -j 4

RUN cd R-${R_VERSION} && make install

RUN rm -rf /usr/local/lib/R/library/translations
RUN rm -rf /usr/local/lib/R/doc
RUN mkdir -p /usr/local/lib/R/doc/html
RUN find /usr/local/lib/R/library -name help | xargs rm -rf

RUN touch /usr/local/lib/R/doc/html/R.css

# install required R packages:
RUN yum install -y dnf --enablerepo=powertools \
    udunits2-devel \
    openssl-devel \
    sqlite-devel \
    geos-devel \
    proj-devel \
    libcurl-devel \
    git

RUN R -e 'install.packages(c("stars", "jsonlite", "curl", "lubridate"), repos = "https://cloud.r-project.org")'
RUN pip3 install rpy2 xarray requests dask

# EP: install UDF test script and run it:
WORKDIR /root
RUN git clone https://github.com/Open-EO/openeo-udf-python-to-r.git
RUN ls openeo-udf-python-to-r
RUN pip install .
# RUN python3 tests/test.py

RUN yum remove -y gcc gcc-c++ gcc-gfortran 


FROM almalinux:8.5 as final

ENV TZ=UTC

COPY --from=build /usr/local /usr/local

COPY --from=build /usr/lib64 /usr/lib64

RUN yum install -y gcc-gfortran zlib bzip2 xz-libs pcre2 bash which
RUN ln -sf /bin/bash /bin/sh

RUN yum install -y epel-release
RUN yum install -y dnf --enablerepo=powertools \
    udunits2 \
    openssl \
    sqlite \
    geos \
    proj

WORKDIR /root

# but this is grosse:
ENV LD_LIBRARY_PATH=/usr/lib64/atlas 
# check R runs:
RUN R -e 'print(1+2)'
# check R can load package stars:
RUN R -e 'library(stars)'

# original:
USER 18585
