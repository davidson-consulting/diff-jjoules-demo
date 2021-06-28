package fr.davidson.diff_jjoules_demo;

import org.powerapi.jjoules.EnergySample;
import org.powerapi.jjoules.jni.Perf;
import org.powerapi.jjoules.rapl.RaplDevice;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.function.Function;

/**
 * @author Benjamin DANGLOT
 * benjamin.danglot@davidson.fr
 * on 21/04/2021
 */
public class InternalList<T> {
    private final List<T> internalList;

    public InternalList(T... elements) {
        this.internalList = new ArrayList<>(Arrays.asList(elements));
    }

    public List<T> map(Function<T, T> operator) {
        final List<T> mappedList = new ArrayList<>();
        for (T t : this.internalList) {
            mappedList.add(operator.apply(t));
        }
        return mappedList;
    }

    public int count() {
        consumeDurations(1E10);
        return this.internalList.size();
    }

    public int count2() {
        return this.internalList.size();
    }

    private static void consumeEnergy(final double energyToConsume) {
        EnergySample energySample = RaplDevice.RAPL.recordEnergy();
        long random = 0L;
        while (energySample.getEnergyReport().get("package|uJ") < energyToConsume) {
            random += new java.util.Random(random).nextLong();
        }
    }

    private static void consumeInstructions(final double instructionsToConsume) {
        if (EnergySample.perf == null) {
            EnergySample.perf = new Perf();
            EnergySample.perf.start();
            System.out.println("START PERF");
        }
        long random = 0L;
        while (EnergySample.perf.read() < instructionsToConsume) {
            random += new java.util.Random(random).nextLong();
        }
    }

    private static void consumeDurations(final double durationsToConsume) {
        EnergySample energySample = RaplDevice.RAPL.recordEnergy();
        long random = 0L;
        while (energySample.getEnergyReport().get("durations|ns") < durationsToConsume) {
            random += new java.util.Random(random).nextLong();
        }
    }
}