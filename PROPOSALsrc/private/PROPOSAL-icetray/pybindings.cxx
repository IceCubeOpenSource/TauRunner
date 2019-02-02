
#include "PROPOSAL-icetray/I3PropagatorServicePROPOSAL.h"
#include "PROPOSAL-icetray/SimplePropagator.h"
#include "icetray/load_project.h"

I3_PYTHON_MODULE(PROPOSAL)
{
    load_project("PROPOSAL", false);

    using namespace PROPOSAL;
    using namespace boost::python;
    import("icecube.dataclasses");
    import("icecube.sim_services");

    class_<I3PropagatorServicePROPOSAL,
           boost::shared_ptr<I3PropagatorServicePROPOSAL>,
           bases<I3PropagatorService>,
           boost::noncopyable>(
        "I3PropagatorServicePROPOSAL",
        init<std::string, I3Particle::ParticleType, double>(
            (arg("config_file")           = I3PropagatorServicePROPOSAL::GetDefaultConfigFile(),
             arg("final_stochastic_loss") = I3Particle::unknown,
             arg("distance_to_propagate") = 1e20),
            ":param config_file: Path to the configuration file\n"
            ":param final_stochastic_loss: Finalize the propagation with a stochastic loss of the given type. Use a "
            "ParticleType different from unknown to enable this feature. The data are stored in a particle of that given type.\n"
            ":param distance_to_propagate: Stop the propagation if this propagation length is reached\n"))
        .def("register_particletype", &I3PropagatorServicePROPOSAL::RegisterParticleType);

    class_<SimplePropagator, boost::shared_ptr<SimplePropagator>, boost::noncopyable>(
        "SimplePropagator",
        init<I3Particle::ParticleType, std::string, double, double, double, I3Particle::ParticleType>((arg("type")   = I3Particle::MuMinus,
                                                                             arg("medium") = "ice",
                                                                             arg("ecut")   = -1.0,
                                                                             arg("vcut")   = -1.0,
                                                                             arg("rho")    = -1.0,
                                                                             arg("final_stochastic_loss") = I3Particle::unknown)))
        .def("set_seed", &SimplePropagator::SetSeed)
        .def("propagate",
             &SimplePropagator::propagate,
             (args("p"), arg("distance"), arg("secondaries") = boost::shared_ptr<std::vector<I3Particle> >()));
}