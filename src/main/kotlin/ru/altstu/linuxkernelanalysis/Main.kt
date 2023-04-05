package ru.altstu.linuxkernelanalysis

fun main(args: Array<String>) {
    val boopa = WordMatcher(true)
    boopa.addNewMessage("fixed dore")
    boopa.addNewMessage("fixed core")
    boopa.addNewMessage("boopa")


    println(boopa.buildMessageDistances())
}