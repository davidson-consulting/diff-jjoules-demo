# Diff-Jjoules Demo

This project aims at showing how Diff-JJoules works and what can be done.

## Diff-JJoules

Diff-JJoules aims at measuring the impact of code changes (commit) on energy consumption.

The algorithm is as follow : 

1. Clone twice the project
2. Each clone is set to a specific version, for example two sucessive commits
3. Execute the tests on the two versions and select the tests as follow :
    * Select the tests in the version before the commit that execute the lines that have been removed by the commit
    * Select the tests in the version after the commit that execute the lines that have been added by the commit
4. Instrument the tests that have been selected with special annotations to measure the energy consumption of each test
5. Execute the test on the two versions

## Prerequisites

### Install JJoules

```sh
git clone https://github.com/Mamadou59/j-joules
cd j-joules
mvn clean install -DskipTests
```

### Install JUnit-JJoules

```sh
git clone https://github.com/davidson-consulting/junit-jjoules
```

Generate the shared library, by replacing `<absolute-path>` by the absolute path, and `<JAVA_HOME>` by your correct `JAVA_HOME`:

```sh
cd junit-jjoules/src/main/c
export JAVA_HOME=<JAVA_HOME>
make
LD_LIBRARY_PATH=<absolute-path>/junit-jjoules/src/main/c/lib/
export LD_LIBRARY_PATH
```

Then, install JUnit-JJoules:

```sh
cd ../../..
mvn clean install -DskipTests
```

### Install Diff-JJoules

```sh
https://github.com/davidson-consulting/diff-jjoules
cd diff-jjoules
mvn clean install -DskipTests
```

### Install DSpot-diff-test-selection

```sh
git clone https://github.com/STAMP-project/dspot.git
cd dspot
mvn clean install -DskipTests
```

### Set up permission to RAPL and perf_event

```sh
sudo chmod -R 777 /sys/devices/virtual/powercap/intel-rapl/intel-rapl:*
sudo -i
echo -1 > /proc/sys/kernel/perf_event_paranoid
```

### Configure Compilation for Warming up the JVM with Maven

```sh
export MAVEN_OPTS="-XX:CompileThreshold=1 -XX:-TieredCompilation"
```

## Demo

### Scenario

In this demo, the code changes are the following:

```diff
public List<T> map(Function<T, T> operator) {
    final List<T> mappedList = new ArrayList<>();
+    for (T t : this.internalList) {
+        mappedList.add(operator.apply(t));
+    }
-    for (int i = 0; i < this.internalList.size(); i++) {
-        mappedList.add(operator.apply(this.internalList.get(i)));
-    }
    return mappedList;
}
```

### Instrumenation Example

```diff
+@EnergyTest
-@Test
void testMapEmptyList() {
    final InternalList<Integer> emptyList = new InternalList<>();
    final List<Integer> map = emptyList.map(integer -> 2 * integer);
    assertTrue(map.isEmpty());
}
```

### Run 

To execute the demo, run the python script as follow:

```python
python3 src/main/python/demo.py
```

You should observe something like : 

```txt
fr.davidson.diff_jjoules_demo.InternalListTest-testMapEmptyList.json -63836.0
fr.davidson.diff_jjoules_demo.InternalListTest-testMapOneElement.json -18369.0
fr.davidson.diff_jjoules_demo.InternalListTest-testMapMultipleElement.json 16857.5
```