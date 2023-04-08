package ru.altstu.linuxkernelanalysis

import org.eclipse.jgit.lib.Repository
import org.eclipse.jgit.storage.file.FileRepositoryBuilder
import java.io.File
import java.util.*

fun main(args: Array<String>) {
    val repoDir = File("D:\\linux\\linux\\.git")
    val builder: FileRepositoryBuilder = FileRepositoryBuilder()
        .setGitDir(repoDir)
        .readEnvironment()
        .findGitDir()

    val repo: Repository = builder.build()

    val calendar = Calendar.getInstance()
    calendar.add(Calendar.WEEK_OF_MONTH, -8)
    val oneMonthAgo = calendar.time

    val scaner = RepositoryScanner(WordMatcher(true), repo, oneMonthAgo,Date(Long.MAX_VALUE))

    val result = scaner.analyze()


    for( r in result){
        println(r.toString())
    }
}