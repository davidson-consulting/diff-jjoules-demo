package fr.davidson.diff_jjoules_demo;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Random;
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
        consumeEnergy(2000);
        return this.internalList.size();
    }

    public int count2() {
        consumeEnergy(2000);
        return this.internalList.size();
    }

    private static long consumeEnergy(final long timeElapsed) {
        long current = new Random().nextLong();
        final long startingTime = System.currentTimeMillis();
        while (System.currentTimeMillis() - startingTime < timeElapsed) {
            current += new Random(current).nextLong();
        }
        return current;
    }

}
