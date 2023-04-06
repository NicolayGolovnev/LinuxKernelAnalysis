package ru.altstu.linuxkernelanalysis

import org.eclipse.jgit.api.Git
import org.eclipse.jgit.diff.*
import org.eclipse.jgit.lib.Constants
import org.eclipse.jgit.lib.Repository
import org.eclipse.jgit.patch.FileHeader
import org.eclipse.jgit.revwalk.RevCommit
import org.eclipse.jgit.revwalk.RevWalk
import org.eclipse.jgit.util.io.DisabledOutputStream
import ru.altstu.linuxkernelanalysis.SortUtil.sortByDescValue
import java.io.IOException
import me.tongfei.progressbar.ProgressBar

import java.util.*

class RepositoryScanner(
    val msgMatcher: MessageMatcher,
    val repository: Repository,
    val startDate: Date,
    val endDate: Date
) {
    private val git: Git = Git(repository)
    private var gitPath: String? = null

    fun isCommitInBranch(commit: RevCommit, branchName: String): Boolean {
        val walk = RevWalk(this.repository)

        val targetCommit: RevCommit = walk.parseCommit(
            repository.resolve(commit.name)
        )

        return repository.allRefs.entries.find { (key, value) ->
            key.startsWith(Constants.R_HEADS) &&
                    walk.isMergedInto(targetCommit, walk.parseCommit(value.objectId)) &&
                    branchName == value.name
        } != null
    }

    fun getCommits(): Iterable<RevCommit> {
        return if (gitPath == null)
            git.log().all().call()
        else
            git.log()
                .add(git.repository.resolve(Constants.HEAD))
                .addPath(gitPath).call()
    }

    fun analyze(): List<IMessange> {
        val branches = git.branchList().call()

        for (branch in branches) {
            val branchName = branch.name
            val commits = getCommits().filter { commit ->
                Date(commit.commitTime * 1000L).after(startDate) &&
                        Date(commit.commitTime * 1000L).before(endDate) &&
                        commit.parentCount > 0
            }
            val progressBar = ProgressBar("Repository scan", commits.size.toLong())

            for (commit in commits) {
                if (isCommitInBranch(commit, branchName)) {
                    val lines = commit.fullMessage
                        .split("\n".toRegex())
                        .dropLastWhile { it.isEmpty() }
                        .toTypedArray()
                    lines
                        .filter { line -> isFixMessage(line) }
                        .map { line -> msgMatcher.addNewMessage(line) }
                }
                progressBar.step()
            }
        }
        return msgMatcher.getResult(20)
    }

    fun isFixMessage(message: String): Boolean {
        return "fix" in message
    }
}