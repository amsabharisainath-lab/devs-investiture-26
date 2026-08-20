import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";

export default function Register() {
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [department, setDepartment] = useState("");
  const [year, setYear] = useState("");
  const [registerNumber, setRegisterNumber] = useState("");

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    console.log({
      name,
      department,
      year,
      registerNumber,
    });

    navigate("/event");
  };

  return (
    <main className="register-page">
      <section className="register-container">

        <div className="register-heading">
          <div className="brand">DEVS</div>

          <h1>INVESTITURE-26</h1>
        </div>

        <form
          className="register-form"
          onSubmit={handleSubmit}
        >

          <label htmlFor="name">
            NAME

            <input
              id="name"
              type="text"
              value={name}
              onChange={(event) =>
                setName(event.target.value)
              }
              required
            />
          </label>


          <label htmlFor="department">
            DEPARTMENT

            <input
              id="department"
              type="text"
              value={department}
              onChange={(event) =>
                setDepartment(event.target.value)
              }
              required
            />
          </label>


          <label htmlFor="year">
            YEAR

            <input
              id="year"
              type="text"
              value={year}
              onChange={(event) =>
                setYear(event.target.value)
              }
              required
            />
          </label>


          <label htmlFor="register-number">
            REGISTER NUMBER

            <input
              id="register-number"
              type="text"
              value={registerNumber}
              onChange={(event) =>
                setRegisterNumber(event.target.value)
              }
              required
            />
          </label>


          <button
            className="register-button"
            type="submit"
          >
            REGISTER
          </button>

        </form>

      </section>
    </main>
  );
}