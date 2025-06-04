#include <iostream>
#include <fstream>
#include <sstream>
#include <cstdlib>
#include <string>

bool file_exists(const std::string& name) {
    std::ifstream f(name.c_str());
    return f.good();
}

std::string compile_code(const std::string& source_path, const std::string& exe_path) {
    std::string cmd = "g++ \"" + source_path + "\" -o \"" + exe_path + "\" 2> compile_errors.txt";
    int result = system(cmd.c_str());
    if (result != 0) {
        std::ifstream err("compile_errors.txt");
        std::stringstream buffer;
        buffer << err.rdbuf();
        return "[COMPILATION ERROR]\n" + buffer.str();
    }
    return "";
}

std::string run_test(const std::string& exe_path, const std::string& input_file, const std::string& expected_output_file, int test_num) {
    std::string output = "student_output.txt";
    std::string cmd = "./" + exe_path + " < " + input_file + " > " + output;


    int result = system(cmd.c_str());
    if (result != 0) {
        return "[TEST " + std::to_string(test_num) + "] Runtime error\n";
    }

    std::ifstream student_out(output);
    std::ifstream expected_out(expected_output_file);

    std::string s_line, e_line;
    int line_num = 1;
    while (std::getline(student_out, s_line) && std::getline(expected_out, e_line)) {
        if (!s_line.empty() && s_line.back() == '\r')
            s_line.pop_back();
        if (!e_line.empty() && e_line.back() == '\r')
            e_line.pop_back();
        if (s_line != e_line) {
            return "[TEST " + std::to_string(test_num) + "] Failed at line " + std::to_string(line_num) + "\n";
        }
        line_num++;
    }

    if ((std::getline(student_out, s_line)) || (std::getline(expected_out, e_line))) {
        return "[TEST " + std::to_string(test_num) + "] Output length mismatch\n";
    }

    return "[TEST " + std::to_string(test_num) + "] Passed\n";
}

int main(int argc, char* argv[]) {
    int passed = 0;
    int total  = 0;
    int test_num = 1;
    if (argc != 3) {
        std::cerr << "Usage: checker <file.cpp> <lab_id>\n";
        return 1;
    }

    std::string source_path = argv[1];
    std::string lab_id = argv[2];
    std::string exe_path = "student_program.exe";

    std::string result = compile_code(source_path, exe_path);
    if (!result.empty()) {
        std::cout << result;
        return 1;
    } else {
        std::cout << "[COMPILATION SUCCESS]\n";
    }


    while (true) {
        std::string input_file  = "tests/" + lab_id + "/input"  + std::to_string(test_num) + ".txt";
        std::string output_file = "tests/" + lab_id + "/output" + std::to_string(test_num) + ".txt";

        if (!file_exists(input_file) || !file_exists(output_file)) {
            break;                     // тестов больше нет
        }

        std::string res = run_test(exe_path, input_file, output_file, test_num);
        std::cout << res;              // печатаем результат каждого теста

        ++total;
        if (res.find("Passed") != std::string::npos) {
            ++passed;                  // считаем успешные
        }
        ++test_num;
    }

    std::cout << "\n[SUMMARY] " << passed << " / " << total << " tests passed\n";
    return 0;
}
