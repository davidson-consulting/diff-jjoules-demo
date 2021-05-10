package fr.davidson.diff_jjoules_demo;

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
        for (int i = 0 ; i < this.internalList.size(); i++) {
            mappedList.add(operator.apply(this.internalList.get(i)));
        }
        return mappedList;
    }

    public int count() {
        return this.internalList.size();
    }

}
