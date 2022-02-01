package fr.davidson.diff_jjoules_demo;

/**
 * @author Benjamin DANGLOT
 * benjamin.danglot@davidson.fr
 * on 21/04/2021
 */
public class SourceCode {

    public void neverChangedMethod() {
        System.out.println("This method is never changed");
    }

    public void methodOne() {
        consume(2000);
        consume(2000);
    }

    public void methodTwo() {
        consume(2000);
    }

    private void consume(long millisToConsume) {
        final long startingTime = System.currentTimeMillis();
        long currentTime = System.currentTimeMillis();
        while (currentTime - startingTime < millisToConsume) {
            currentTime = System.currentTimeMillis();
        }
    }

}