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
                    Test  Value_n  Value_p Variation  Measure
0        testMapEmptyList        0     3418    31.29% Energy
1       testMapOneElement      -61        0    -0.57% Energy
2  testMapMultipleElement        0     2441    19.23% Energy
3        testMapEmptyList        0     6298     1.46% Instructions
4       testMapOneElement        0      568     0.14% Instructions
5  testMapMultipleElement    -9840        0    -1.49% Instructions
6        testMapEmptyList        0   443216    25.66% Durations
7       testMapOneElement   -69384        0    -4.78% Durations
8  testMapMultipleElement   -80080        0    -4.26% Durations
```

For each Measure : Energy (uJ), Instructions (#) and Durations (ns), this table gives for each unit test
(testMapEmptyList, testMapOneElement, testMapMultipleElement), the delta (v2 - v1). 
Value_n and Value_p are equals to delta or 0 depending on the sign of the delta (`< 0` for Value_n, and `> 0` for Value_p).
The variation is the proportion of the delta against the value of the v1 : (delta * v1) / 100.
This is done to reveal how much the commit impacts the indicators of the program.

In the folder `target/demo-output/` you can find all the data stored : for each version `v1` and `v2`, there is a folder.
Inside each folder `target/demo-output/v1` and `target/demo-output/v2`, there is one folder per iteration.
Inside each iteration folder, _e.g._ `target/demo-output/v1/1`, there are several json files that reports the value monitored by
`JJoules`.
Inside the folder `target/demo-output/`, there are also two histogram, such as the following :

![](src/main/resource/graph_all.png)
![](src/main/resource/graph_instr_energy.png)

That reports graphically the computed deltas. 
If the delta is negative, it means that v1 consumes more than v2 (because `v2 - v1 < 0, v2 < v1`).
If the delta is positive, it means that v1 consumes less than v2 (because `v2 - v1 > 0, v2 > v1`).