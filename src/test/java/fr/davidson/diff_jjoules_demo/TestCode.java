package fr.davidson.diff_jjoules_demo;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * @author Benjamin DANGLOT
 * benjamin.danglot@davidson.fr
 * on 21/04/2021
 */
public class TestCode {

    @Test
    void testNeverChangedMethod() {
        final SourceCode sourceCode = new SourceCode();
        sourceCode.neverChangedMethod();
        assertTrue(true);
    }

    @Test
    void testMethodOne() {
        final SourceCode sourceCode = new SourceCode();
        sourceCode.methodOne();
        assertTrue(true);
    }

    @Test
    void testMethodTwo() {
        final SourceCode sourceCode = new SourceCode();
        sourceCode.methodTwo();
        assertTrue(true);
    }

}
