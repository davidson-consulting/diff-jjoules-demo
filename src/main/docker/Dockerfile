
FROM maven:3.6.0-jdk-11-slim

RUN mvn --version
RUN java -version
RUN apt update
RUN apt-get install git g++ make linux-perf --yes

RUN git clone https://github.com/STAMP-project/dspot.git /tmp/dspot
RUN mvn clean install -DskipTests -f /tmp/dspot/pom.xml

RUN git clone https://github.com/Mamadou59/j-joules /tmp/j-joules
RUN mvn clean install -DskipTests -f /tmp/j-joules/pom.xml

RUN git clone https://@github.com/davidson-consulting/junit-jjoules /tmp/junit-jjoules
RUN export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
RUN cd /tmp/junit-jjoules/src/main/c && ls && mkdir lib && ls && make
RUN LD_LIBRARY_PATH=/tmp/junit-jjoules/src/main/c/lib/
RUN export LD_LIBRARY_PATH
RUN mvn clean install -DskipTests -f /tmp/junit-jjoules/pom.xml

RUN git clone https://github.com/INRIA/spoon/ /tmp/spoon
RUN cd /tmp/spoon && mvn clean install -DskipTests

RUN rm -rf /tmp/diff-jjoules
RUN git clone https://@github.com/davidson-consulting/diff-jjoules /tmp/diff-jjoules
RUN mvn clean install -DskipTests -f /tmp/diff-jjoules/pom.xml

RUN git clone https://github.com/davidson-consulting/untare-jjoules.git /tmp/untare-jjoules
RUN mvn clean install -DskipTests -f /tmp/untare-jjoules/pom.xml

RUN git clone https://@github.com/davidson-consulting/diff-jjoules-demo.git /tmp/v1
RUN mvn -Drat.skip=true -Djacoco.skip=true -Danimal.sniffer.skip=true -f  /tmp/v1/pom.xml clean install -DskipTests dependency:build-classpath -Dmdep.outputFile=classpath
RUN cp -r /tmp/v1 /tmp/v2
RUN mvn -Drat.skip=true -Djacoco.skip=true -Danimal.sniffer.skip=true -f  /tmp/v2/pom.xml clean install -DskipTests dependency:build-classpath -Dmdep.outputFile=classpath fr.davidson:untare-jjoules:mutate -Dmethod-names-per-full-qualified-names=methodNames.csv

RUN mvn -Drat.skip=true -Djacoco.skip=true -Danimal.sniffer.skip=true \
    -f /tmp/v1/pom.xml clean eu.stamp-project:dspot-diff-test-selection:3.1.1-SNAPSHOT:list \
    -Dpath-dir-second-version=/tmp/v2 fr.davidson:diff-jjoules:instrument -Dtests-list=testsThatExecuteTheChange.csv \
    -Dclasspath-path-v2=classpath -Dclasspath-path-v1=classpath 

COPY run.sh /tmp/run.sh
ENTRYPOINT [ "/tmp/run.sh" ]