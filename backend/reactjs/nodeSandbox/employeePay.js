const getNonSalaryHourlyRate = (location) => {
    
    const nationalMinimumWage = 7.5;
    const mapOfLocationToRate = {
        'AZ': 15,
        'NY': 30,
        'TX': 2,
    };

    return mapOfLocationToRate[location] || nationalMinimumWage;
}


const getSalaryHourlyRate = (salaryPerYear) => {
    const numberOfWorksHoursInAYear = 40*52;

    return salaryPerYear / numberOfWorksHoursInAYear;
}

const getNonSalaryPayAmount = (numberOfHoursWorked, location) => numberOfHoursWorked * getNonSalaryHourlyRate(location);

const getSalaryPayAmount = (numberOfHoursWorked, salaryPerYear) => numberOfHoursWorked * getSalaryHourlyRate(salaryPerYear);

const getPayAmountCalculation = (numberOfHoursWorked, hourlyRate) => {
    const hourlyRate = isSalaried ? getSalaryHourlyRate(salaryPerYear) : getNonSalaryHourlyRate(location);

    return numberOfHoursWorked * hourlyRate;
};

const getNonSalaryPayAmountFunction = (location) => (numberOfHoursWorked) => getNonSalaryPayAmount(numberOfHoursWorked, location);

const getSalaryPayAmountFunction = (salaryPerYear) => (numberOfHoursWorked) => getSalaryPayAmount(numberOfHoursWorked, salaryPerYear);





