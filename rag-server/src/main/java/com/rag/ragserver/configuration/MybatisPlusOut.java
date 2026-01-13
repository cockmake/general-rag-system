package com.rag.ragserver.configuration;

import org.apache.ibatis.logging.Log;

public class MybatisPlusOut implements Log {

    public MybatisPlusOut(String clazz) {
        System.out.println("MybatisPlusOut::" + clazz);
    }

    public boolean isDebugEnabled() {
        return true;
    }

    public boolean isTraceEnabled() {
        return true;
    }

    public void error(String s, Throwable e) {
        System.err.println(s);
        e.printStackTrace(System.err);
    }

    public void error(String s) {
        System.err.println("MybatisPlusOut::" + s);
    }

    public void debug(String s) {
        System.out.println("MybatisPlusOut::" + s);
    }

    public void trace(String s) {
        System.out.println("MybatisPlusOut::" + s);
    }

    public void warn(String s) {
        System.out.println("MybatisPlusOut::" + s);
    }
}
